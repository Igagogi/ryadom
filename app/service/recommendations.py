from fastapi import HTTPException

from app.schemas.recommendations import RecommendationAIResponse
from app.service import ai
from app.service.scenarios import find_scenario
from app.utils.rate_limit import check_and_increment


async def generate_recommendation(age: int, situation: str, ip: str) -> RecommendationAIResponse:

    scenario = find_scenario(age, situation)

    if scenario is not None:
        return RecommendationAIResponse(
            steps=scenario.steps,
            phrase=scenario.phrase,
            avoid=scenario.avoid,
            if_not_helped=scenario.if_not_helped
        )

    if not check_and_increment(ip):
        raise HTTPException(
            status_code=429,
            detail="Бесплатный лимит AI-запросов исчерпан. Зарегистрируйтесь, чтобы продолжить."            
        )

    try:
        result = await ai.generate_ai_recommendation(age, situation)
    except ai.AIServiceError:
        raise HTTPException(
            status_code=503,
            detail="Сервис рекомендаций временно недоступен"
        )

    return result