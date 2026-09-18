from fastapi import APIRouter, Request

from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.service.recommendations import generate_recommendation

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(recommendation: RecommendationRequest, request: Request):
    
    result = await generate_recommendation(recommendation.age, recommendation.situation, request.client.host)

    return RecommendationResponse(
        steps=result.steps, 
        phrase=result.phrase, 
        avoid=result.avoid, 
        if_not_helped=result.if_not_helped
        )