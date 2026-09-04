from app.schemas.recommendations import RecommendationAIResponse
from app.service.scenarios import find_scenario
from app.service import ai


def generate_recommendation(age: int, situation: str) -> RecommendationAIResponse:

    scenario = find_scenario(age, situation)

    if scenario is not None:
        return RecommendationAIResponse(
            steps=scenario.steps,
            phrase=scenario.phrase,
            avoid=scenario.avoid,
            if_not_helped=scenario.if_not_helped
        )
    
    result = ai.generate_ai_recommendation(age, situation)

    return result