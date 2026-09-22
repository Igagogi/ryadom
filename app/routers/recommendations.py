from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_optional_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.service.recommendations import generate_recommendation

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    recommendation: RecommendationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    result = await generate_recommendation(
        recommendation.age,
        recommendation.category,
        recommendation.subcategory,
        recommendation.place,
        request.client.host,
        current_user,
        db,
    )

    return RecommendationResponse(
        title=result.title,
        steps=result.steps,
        phrase=result.phrase,
        avoid=result.avoid,
        if_not_helped=result.if_not_helped,
    )