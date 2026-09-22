from fastapi import HTTPException

from app.db.models import User
from app.schemas.story import StoryAIResponse, StoryDuration, StoryMood
from app.service.ai import AIServiceError, generate_ai_story
from app.utils.rate_limit import check_and_increment


async def generate_story(
    age: int,
    name: str | None,
    mood: StoryMood,
    character: str | None,
    duration: StoryDuration,
    ip: str,
    current_user: User | None,
) -> StoryAIResponse:

    if current_user is None:
        if not check_and_increment(ip, limit=1):
            raise HTTPException(
                status_code=429,
                detail="Бесплатный лимит AI-запросов исчерпан. Зарегистрируйтесь, чтобы продолжить.",
            )

    try:
        result = await generate_ai_story(
            age=age,
            name=name,
            mood=mood,
            character=character,
            duration=duration,
        )
    except AIServiceError:
        raise HTTPException(
            status_code=503, 
            detail="Сервис генераций историй временно недоступен."
        )

    return result