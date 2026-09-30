from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.prompts.recommendations import RECOMMENDATIONS_SYSTEM_PROMPT
from app.ai.service import AIService, AIServiceError
from app.constants.scenarios import (
    CATEGORY_LABELS,
    PLACE_LABELS,
    SUBCATEGORY_LABELS,
)
from app.db.models import User
from app.repository.scenarios import get_scenario
from app.schemas.recommendations import RecommendationAIResponse
from app.utils.rate_limit import check_and_increment


async def generate_recommendation(
    age: int,
    category: str,
    subcategory: str,
    place: str | None,
    ip: str,
    current_user: User | None,
    db: Session,
    ai_service: AIService,
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
        if not check_and_increment(
            ip,
            operation="recommendations",
        ):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Бесплатный лимит AI-запросов исчерпан. "
                    "Зарегистрируйтесь, чтобы продолжить."
                ),
            )

    category_text = CATEGORY_LABELS.get(category, category)
    subcategory_text = SUBCATEGORY_LABELS.get(
        subcategory,
        subcategory,
    )
    place_text = PLACE_LABELS.get(
        place,
        place or "место не указано",
    )

    user_prompt = (
        f"Возраст ребёнка: {age}. "
        f"Категория ситуации: {category_text}. "
        f"Подкатегория ситуации: {subcategory_text}. "
        f"Место: {place_text}."
    )

    try:
        result = await ai_service.generate(
            system_prompt=RECOMMENDATIONS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RecommendationAIResponse,
        )
    except AIServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail="Сервис рекомендаций временно недоступен",
        ) from exc

    return result