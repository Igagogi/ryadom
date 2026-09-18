from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_optional_current_user
from app.db.models import User
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.service.recommendations import generate_recommendation

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    recommendation: RecommendationRequest,
    request: Request,
    current_user: User | None = Depends(get_optional_current_user),
):
    result = await generate_recommendation(
        recommendation.age,
        recommendation.situation,
        request.client.host,
        current_user,
    )

    return RecommendationResponse(
        steps=result.steps,
        phrase=result.phrase,
        avoid=result.avoid,
        if_not_helped=result.if_not_helped,
    )