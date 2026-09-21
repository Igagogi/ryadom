from fastapi import HTTPException

from app.db.models import User
from app.schemas.activities import ActivityAIResponse, ActivityResponse
from app.service.activity_scenarios import find_activity_scenario
from app.service.ai import AIServiceError, generate_ai_activity
from app.utils.rate_limit import check_and_increment


async def generate_activity(
    age: int,
    time: int,
    place: str,
    available_items: list[str],
    ip: str,
    current_user: User | None,
) -> ActivityResponse | ActivityAIResponse:

    scenario = find_activity_scenario(
        age,
        time,
        place,
        available_items,
    )

    if scenario is not None:
        return scenario

    if current_user is None:
        if not check_and_increment(ip):
            raise HTTPException(
                status_code=429,
                detail="Бесплатный лимит AI-запросов исчерпан. Зарегистрируйтесь, чтобы продолжить.",
            )

    try:
        result = await generate_ai_activity(
            age=age,
            time=time,
            place=place,
            available_items=available_items,
        )

        if result.duration > time:
            result = await generate_ai_activity(
                age=age,
                time=time,
                place=place,
                available_items=available_items,
                correction=(
                    f"Предыдущий вариант не подходит: "
                    f"его продолжительность {result.duration} минут, "
                    f"а пользователю доступно только {time} минут. "
                    f"Сгенерируй новый вариант. "
                    f"Продолжительность duration должна быть не больше {time} минут."
                ),
            )

        if result.duration > time:
            raise AIServiceError(
                "AI не смог сформировать подходящую активность"
            )

    except AIServiceError:
        raise HTTPException(
            status_code=503,
            detail="Сервис рекомендаций временно недоступен",
        )

    return result