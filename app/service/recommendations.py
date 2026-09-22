from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import User
from app.repository.scenarios import get_scenario
from app.schemas.recommendations import RecommendationAIResponse
from app.service import ai
from app.utils.rate_limit import check_and_increment


async def generate_recommendation(
    age: int,
    category: str,
    subcategory: str,
    place: str | None,
    ip: str,
    current_user: User | None,
    db: Session,
) -> RecommendationAIResponse:

    if category != "other":
        scenario = get_scenario(
            db=db,
            category=category,
            subcategory=subcategory,
            age=age,
            place=place,
        )

        if scenario is not None:
            return RecommendationAIResponse(
                title=scenario.title,
                steps=scenario.steps,
                phrase=scenario.phrase,
                avoid=scenario.avoid,
                if_not_helped=scenario.if_not_helped,
            )

    if current_user is None:
        if not check_and_increment(ip, operation="recommendations"):
            raise HTTPException(
                status_code=429,
                detail="Бесплатный лимит AI-запросов исчерпан. Зарегистрируйтесь, чтобы продолжить.",
            )

    try:
        result = await ai.generate_ai_recommendation(
            age,
            category,
            subcategory,
            place,
        )
    except ai.AIServiceError:
        raise HTTPException(
            status_code=503,
            detail="Сервис рекомендаций временно недоступен",
        )

    return result
