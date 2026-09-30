from fastapi import APIRouter, Depends, Request

from app.ai.service import AIService
from app.core.ai import get_ai_service
from app.core.dependencies import get_optional_current_user
from app.db.models import User
from app.schemas.story import StoryRequest, StoryResponse
from app.service.stories import generate_story

router = APIRouter()


@router.post("/stories", response_model=StoryResponse)
async def create_story(
    story_request: StoryRequest,
    request: Request,
    current_user: User | None = Depends(get_optional_current_user),
    ai_service: AIService = Depends(get_ai_service),
):
    result = await generate_story(
        age=story_request.age,
        name=story_request.name,
        mood=story_request.mood,
        character=story_request.character,
        duration=story_request.duration,
        ip=request.client.host,
        current_user=current_user,
        ai_service=ai_service,
    )

    return StoryResponse(
        title=result.title,
        story=result.story,
    )