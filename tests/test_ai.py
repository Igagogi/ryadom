from unittest.mock import AsyncMock

import pytest

from app.ai.base import LLMProvider
from app.ai.service import AIService, AIServiceError
from app.schemas.recommendations import RecommendationAIResponse


@pytest.mark.anyio
async def test_ai_service_invalid_json():
    """AIService возвращает ошибку при некорректном JSON."""

    mock_provider = AsyncMock(spec=LLMProvider)
    mock_provider.generate.return_value = "это не JSON"

    ai_service = AIService(mock_provider)

    with pytest.raises(AIServiceError):
        await ai_service.generate(
            system_prompt="test",
            user_prompt="test",
            response_model=RecommendationAIResponse,
        )


@pytest.mark.anyio
async def test_ai_service_invalid_schema():
    """AIService возвращает ошибку при JSON, не соответствующем схеме."""

    mock_provider = AsyncMock(spec=LLMProvider)
    mock_provider.generate.return_value = """
    {
        "steps": ["Успокойте ребёнка"],
        "phrase": "Давай попробуем вместе",
        "avoid": ["Не кричать"]
    }
    """

    ai_service = AIService(mock_provider)

    with pytest.raises(AIServiceError):
        await ai_service.generate(
            system_prompt="test",
            user_prompt="test",
            response_model=RecommendationAIResponse,
        )