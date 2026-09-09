from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.recommendations import RecommendationAIResponse
from app.service.ai import AIServiceError
from app.service.recommendations import generate_recommendation


@pytest.mark.anyio
async def test_generate_recommendation_with_scenario():
    """Тестирование генерации рекомендации с использованием сценария."""
    age = 4
    situation = "не хочет спать"

    mock_ai = Mock()

    mock_ai.generate_ai_recommendation.return_value = RecommendationAIResponse(
        steps=["Step 1", "Step 2"],
        phrase="This is a test phrase.",
        avoid=["Avoid 1", "Avoid 2"],
        if_not_helped="This is a test if_not_helped."
    )

    with patch("app.service.recommendations.ai.generate_ai_recommendation", new=mock_ai.generate_ai_recommendation):
        result = await generate_recommendation(age, situation)
        mock_ai.generate_ai_recommendation.assert_not_called()

    assert result is not None
    assert result.phrase == "Сейчас время готовиться ко сну. Давай вместе закончим наш день."

@pytest.mark.anyio
async def test_generate_recommendation_with_ai():
    """Тестирование генерации рекомендации с использованием AI."""
    age = 2
    situation = "ребёнок боится идти в детский сад"

    mock_ai = AsyncMock()
    
    mock_ai.generate_ai_recommendation.return_value = RecommendationAIResponse(
        steps=["Step 1", "Step 2"],
        phrase="This is a test phrase.",
        avoid=["Avoid 1", "Avoid 2"],
        if_not_helped="This is a test if_not_helped."
        )

    with patch("app.service.recommendations.ai.generate_ai_recommendation", new=mock_ai.generate_ai_recommendation):
        result = await generate_recommendation(age, situation)
        mock_ai.generate_ai_recommendation.assert_awaited_once_with(age, situation)

    assert result is not None
    assert result.phrase == "This is a test phrase."

def test_recommendations_endpoint_with_scenario():
    """Тестирование эндпоинта /recommendations с использованием сценария."""
    client = TestClient(app)

    response = client.post("/recommendations", json={
        "age": 4,
        "situation": "не хочет спать"
        })

    assert response.status_code == 200

    data = response.json()

    assert "steps" in data
    assert "phrase" in data
    assert "avoid" in data
    assert "if_not_helped" in data

    assert isinstance(data["steps"], list)
    assert isinstance(data["phrase"], str)
    assert isinstance(data["avoid"], list)
    assert isinstance(data["if_not_helped"], str)

def test_recommendations_endpoint_with_ai():
    """Тестирование эндпоинта /recommendations с использованием AI."""
    client = TestClient(app)

    mock_result = RecommendationAIResponse(
        steps=["Step 1", "Step 2"],
        phrase="This is a test phrase.",
        avoid=["Avoid 1", "Avoid 2"],
        if_not_helped="This is a test if_not_helped."
    )

    with patch(
        "app.service.recommendations.ai.generate_ai_recommendation",
        return_value=mock_result
    ):
        response = client.post(
            "/recommendations",
            json={
                "age": 2,
                "situation": "ребёнок боится идти в детский сад"
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["steps"] == ["Step 1", "Step 2"]
    assert data["phrase"] == "This is a test phrase."
    assert data["avoid"] == ["Avoid 1", "Avoid 2"]
    assert data["if_not_helped"] == "This is a test if_not_helped."

def test_recommendations_endpoint_invalid_age():
    """Тестирование эндпоинта /recommendations с некорректным типом возраста."""
    client = TestClient(app)

    response = client.post("/recommendations", json={
        "age": "hello",
        "situation": "не хочет спать"
    })

    assert response.status_code == 422

def test_recommendations_endpoint_missing_situation():
    """Тестирование эндпоинта /recommendations с отсутствующим полем situation."""
    client = TestClient(app)

    response = client.post("/recommendations", json={
        "age": 4
    })

    assert response.status_code == 422

def test_recommendations_endpoint_age_out_of_range():
    """Тестирование эндпоинта /recommendations с возрастом вне допустимого диапазона."""
    client = TestClient(app)

    response = client.post("/recommendations", json={
        "age": 0,
        "situation": "не хочет спать"
    })

    assert response.status_code == 422  

    response = client.post("/recommendations", json={
        "age": 17,
        "situation": "не хочет спать"
    })

    assert response.status_code == 422

def test_recommendations_endpoint_valid_age_boundaries():
    """Тестирование эндпоинта /recommendations с граничными значениями возраста."""
    client = TestClient(app)

    mock_result = RecommendationAIResponse(
        steps=["Step 1"],
        phrase="Test phrase",
        avoid=["Avoid 1"],
        if_not_helped="Test if not helped"
    )

    with patch(
        "app.service.recommendations.ai.generate_ai_recommendation",
        return_value=mock_result
    ):
        response = client.post("/recommendations", json={
            "age": 1,
            "situation": "боится идти в детский сад"
        })
        assert response.status_code == 200

        response = client.post("/recommendations", json={
            "age": 16,
            "situation": "боится идти в школу"
        })
        assert response.status_code == 200

def test_recommendations_endpoint_situation_too_short():
    """Тестирование эндпоинта /recommendations с слишком коротким описанием ситуации."""
    client = TestClient(app)

    response = client.post("/recommendations", json={
        "age": 3,
        "situation": "hi"
    })

    assert response.status_code == 422

def test_recommendations_endpoint_situation_empty():
    """Тестирование эндпоинта /recommendations с пустым описанием ситуации."""
    client = TestClient(app)

    response = client.post("/recommendations", json={
        "age": 4,
        "situation": ""
    })

    assert response.status_code == 422

def test_recommendations_endpoint_ai_service_error():
    client = TestClient(app)

    with patch(
        "app.service.recommendations.ai.generate_ai_recommendation",
        side_effect=AIServiceError("AI service error")
    ):
        response = client.post(
            "/recommendations",
            json={
                "age": 6,
                "situation": "ребёнок боится идти в школу"
            }
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Сервис рекомендаций временно недоступен"
    }