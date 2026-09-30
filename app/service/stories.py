from fastapi import HTTPException

from app.ai.prompts.stories import STORY_SYSTEM_PROMPT
from app.ai.service import AIService, AIServiceError
from app.db.models import User
from app.schemas.story import StoryAIResponse, StoryDuration, StoryMood
from app.utils.rate_limit import check_and_increment


async def generate_story(
    age: int,
    name: str | None,
    mood: StoryMood,
    character: str | None,
    duration: StoryDuration,
    ip: str,
    current_user: User | None,
    ai_service: AIService,
) -> StoryAIResponse:

    if current_user is None:
        if not check_and_increment(
            ip,
            operation="stories",
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
        f"Имя ребёнка: {name or 'не указано'}. "
        f"Настроение истории: {mood.value}. "
        f"Предпочитаемый персонаж: {character or 'не указан'}. "
        f"Продолжительность истории: {duration.value}."
    )

    try:
        result = await ai_service.generate(
            system_prompt=STORY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=StoryAIResponse,
        )
    except AIServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail="Сервис генераций историй временно недоступен.",
        ) from exc

    return result