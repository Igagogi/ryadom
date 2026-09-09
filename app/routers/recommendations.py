from fastapi import APIRouter

from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.service.recommendations import generate_recommendation

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(recommendation: RecommendationRequest):
    
    result = await generate_recommendation(recommendation.age, recommendation.situation)

    return RecommendationResponse(
        steps=result.steps, 
        phrase=result.phrase, 
        avoid=result.avoid, 
        if_not_helped=result.if_not_helped
        )