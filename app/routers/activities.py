from fastapi import APIRouter, Depends, Request

from app.ai.service import AIService
from app.core.ai import get_ai_service
from app.core.dependencies import get_optional_current_user
from app.db.models import User
from app.schemas.activities import ActivityAIResponse, ActivityRequest
from app.service.activities import generate_activity

router = APIRouter()


@router.post("/activities", response_model=ActivityAIResponse)
async def create_activity(
    activity_request: ActivityRequest,
    request: Request,
    current_user: User | None = Depends(get_optional_current_user),
    ai_service: AIService = Depends(get_ai_service),
):

    result = await generate_activity(
        age=activity_request.age,
        time=activity_request.time,
        place=activity_request.place,
        available_items=activity_request.available_items,
        ip=request.client.host,
        current_user=current_user,
        ai_service=ai_service,
    )

    return result
