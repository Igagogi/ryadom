from fastapi import HTTPException

from app.ai.prompts.activities import ACTIVITY_SYSTEM_PROMPT
from app.ai.service import AIService, AIServiceError
from app.db.models import User
from app.schemas.activities import ActivityAIResponse
from app.utils.rate_limit import check_and_increment


async def generate_activity(
    age: int,
    time: int,
    place: str,
    available_items: list[str],
    ip: str,
    current_user: User | None,
    ai_service: AIService,
) -> ActivityAIResponse:

    if current_user is None:
        if not check_and_increment(
            ip,
            operation="activities",
            limit=1,
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Бесплатный лимит AI-запросов исчерпан. "
                    "Зарегистрируйтесь, чтобы продолжить."
                ),
            )

    user_prompt = (
        f"Возраст ребёнка: {age}. "
        f"Доступное время: {time} минут. "
        f"Место: {place}. "
        f"Доступные предметы: {', '.join(available_items)}."
    )

    try:
        result = await ai_service.generate(
            system_prompt=ACTIVITY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ActivityAIResponse,
        )

        if result.duration > time:
            correction = (
                f"Предыдущий вариант не подходит: "
                f"его продолжительность {result.duration} минут, "
                f"а пользователю доступно только {time} минут. "
                f"Сгенерируй новый вариант. "
                f"Продолжительность duration должна быть "
                f"не больше {time} минут."
            )

            corrected_prompt = (
                f"{user_prompt} "
                f"Дополнительное требование: {correction}"
            )

            result = await ai_service.generate(
                system_prompt=ACTIVITY_SYSTEM_PROMPT,
                user_prompt=corrected_prompt,
                response_model=ActivityAIResponse,
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