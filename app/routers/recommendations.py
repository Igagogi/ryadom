from fastapi import APIRouter

from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.service.recommendations import generate_recommendation

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
def get_recommendations(recommendation: RecommendationRequest):
    result = generate_recommendation(recommendation.age, recommendation.situation)
    return RecommendationResponse(recommendation=result)