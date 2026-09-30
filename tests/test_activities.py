from unittest.mock import AsyncMock

from app.ai.service import AIService
from app.core.ai import get_ai_service
from app.schemas.activities import ActivityAIResponse


def test_activities_endpoint(client):
    """Тестирование генерации активности через AI."""

    mock_result = ActivityAIResponse(
        title="Тестовая активность",
        description="Тестовое описание",
        steps=["Шаг 1", "Шаг 2"],
        duration=15,
    )

    mock_ai_service = AsyncMock(spec=AIService)
    mock_ai_service.generate.return_value = mock_result

    def override_get_ai_service():
        return mock_ai_service

    from app.main import app

    app.dependency_overrides[get_ai_service] = override_get_ai_service

    response = client.post(
        "/activities",
        json={
            "age": 4,
            "time": 20,
            "place": "home",
            "available_items": ["кубики"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Тестовая активность"
    assert data["description"] == "Тестовое описание"
    assert data["steps"] == ["Шаг 1", "Шаг 2"]
    assert data["duration"] == 15

    mock_ai_service.generate.assert_awaited_once()