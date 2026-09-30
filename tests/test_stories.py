from unittest.mock import AsyncMock

from app.ai.service import AIService
from app.core.ai import get_ai_service
from app.schemas.story import StoryAIResponse


def test_stories_endpoint(client):
    """Тестирование генерации истории через AI."""

    mock_result = StoryAIResponse(
        title="Тестовая история",
        story="Жил-был маленький герой...",
    )

    mock_ai_service = AsyncMock(spec=AIService)
    mock_ai_service.generate.return_value = mock_result

    def override_get_ai_service():
        return mock_ai_service

    from app.main import app

    app.dependency_overrides[get_ai_service] = override_get_ai_service

    response = client.post(
        "/stories",
        json={
            "age": 4,
            "name": "Миша",
            "mood": "funny",
            "character": "зайчик",
            "duration": "short",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Тестовая история"
    assert data["story"] == "Жил-был маленький герой..."

    mock_ai_service.generate.assert_awaited_once()