from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_optional_current_user
from app.db.models import User
from app.schemas.activities import ActivityRequest, ActivityResponse
from app.service.activities import generate_activity

router = APIRouter()

@router.post("/activities", response_model=ActivityResponse)
async def create_activity(
    activity_request: ActivityRequest,
    request: Request,
    current_user: User | None = Depends(get_optional_current_user)
):

    result = await generate_activity(
        age=activity_request.age,
        time=activity_request.time,
        place=activity_request.place,
        available_items=activity_request.available_items,
        ip=request.client.host,
        current_user=current_user,
    )

    return ActivityResponse(
        title=result.title,
        description=result.description,
        steps=result.steps,
        duration=result.duration,
    )