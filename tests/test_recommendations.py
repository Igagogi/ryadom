from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.recommendations import RecommendationAIResponse
from app.service.ai import AIServiceError
from app.utils.rate_limit import request_counts


def test_recommendations_endpoint_with_scenario():
    """Тестирование рекомендации из базы данных."""
    client = TestClient(app)

    response = client.post(
        "/recommendations",
        json={
            "age": 4,
            "category": "refusal",
            "subcategory": "sleep",
            "place": "home",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "title" in data
    assert "steps" in data
    assert "phrase" in data
    assert "avoid" in data
    assert "if_not_helped" in data

    assert isinstance(data["steps"], list)
    assert isinstance(data["phrase"], str)
    assert isinstance(data["avoid"], list)
    assert isinstance(data["if_not_helped"], str)


def test_recommendations_endpoint_with_ai():
    """Тестирование рекомендации через AI."""
    client = TestClient(app)

    mock_result = RecommendationAIResponse(
        title="Тестовая рекомендация",
        steps=["Step 1", "Step 2"],
        phrase="This is a test phrase.",
        avoid=["Avoid 1", "Avoid 2"],
        if_not_helped="This is a test if_not_helped.",
    )

    with patch(
        "app.service.recommendations.ai.generate_ai_recommendation",
        return_value=mock_result,
    ):
        response = client.post(
            "/recommendations",
            json={
                "age": 4,
                "category": "other",
                "subcategory": "unknown",
                "place": "home",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Тестовая рекомендация"
    assert data["steps"] == ["Step 1", "Step 2"]
    assert data["phrase"] == "This is a test phrase."
    assert data["avoid"] == ["Avoid 1", "Avoid 2"]
    assert data["if_not_helped"] == "This is a test if_not_helped."


def test_recommendations_endpoint_invalid_age():
    """Тестирование эндпоинта /recommendations с некорректным типом возраста."""
    client = TestClient(app)

    response = client.post(
        "/recommendations", json={"age": "hello", "situation": "не хочет спать"}
    )

    assert response.status_code == 422


def test_recommendations_endpoint_age_out_of_range():
    """Тестирование эндпоинта /recommendations с возрастом вне допустимого диапазона."""
    client = TestClient(app)

    response = client.post(
        "/recommendations", json={"age": 0, "situation": "не хочет спать"}
    )

    assert response.status_code == 422

    response = client.post(
        "/recommendations", json={"age": 17, "situation": "не хочет спать"}
    )

    assert response.status_code == 422


def test_recommendations_endpoint_valid_age_boundaries():
    """Тестирование граничных значений возраста."""
    client = TestClient(app)

    mock_result = RecommendationAIResponse(
        title="Тестовая рекомендация",
        steps=["Step 1"],
        phrase="Test phrase",
        avoid=["Avoid 1"],
        if_not_helped="Test if not helped",
    )

    with patch(
        "app.service.recommendations.ai.generate_ai_recommendation",
        return_value=mock_result,
    ):
        response = client.post(
            "/recommendations",
            json={
                "age": 1,
                "category": "other",
                "subcategory": "unknown",
                "place": "home",
            },
        )
        assert response.status_code == 200

        response = client.post(
            "/recommendations",
            json={
                "age": 16,
                "category": "other",
                "subcategory": "unknown",
                "place": "home",
            },
        )
        assert response.status_code == 200


def test_recommendations_endpoint_ai_error():
    """Тестирование ошибки AI-сервиса."""
    client = TestClient(app)

    request_counts.clear()

    with patch(
        "app.service.recommendations.ai.generate_ai_recommendation",
        side_effect=AIServiceError("AI error"),
    ):
        response = client.post(
            "/recommendations",
            json={
                "age": 4,
                "category": "other",
                "subcategory": "unknown",
                "place": "home",
            },
        )

    assert response.status_code == 503
