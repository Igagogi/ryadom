from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.ai.service import AIService, AIServiceError
from app.core.ai import get_ai_service
from app.db.models import Scenario
from app.main import app
from app.schemas.recommendations import RecommendationAIResponse
from app.utils.rate_limit import request_counts


def test_recommendations_endpoint_with_scenario(db, client):
    """Тестирование рекомендации из базы данных."""

    scenario = Scenario(
        category="refusal",
        subcategory="sleep",
        age_min=2,
        age_max=6,
        place="home",
        title="Спокойный переход ко сну",
        steps=[
            "Предупредить ребёнка заранее о подготовке ко сну.",
            "Предложить выбрать одну спокойную игру перед сном.",
        ],
        phrase="Сейчас заканчиваем играть и начинаем готовиться ко сну.",
        avoid=[
            "Не угрожать наказанием.",
            "Не повышать голос.",
        ],
        if_not_helped="Дать ребёнку несколько минут на спокойный переход.",
        is_active=True,
    )

    db.add(scenario)
    db.commit()

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

    assert data["title"] == "Спокойный переход ко сну"
    assert data["steps"] == scenario.steps
    assert data["phrase"] == scenario.phrase
    assert data["avoid"] == scenario.avoid
    assert data["if_not_helped"] == scenario.if_not_helped


def test_recommendations_endpoint_with_ai(client):
    """Тестирование рекомендации через AI."""

    mock_result = RecommendationAIResponse(
        title="Тестовая рекомендация",
        steps=["Step 1", "Step 2"],
        phrase="This is a test phrase.",
        avoid=["Avoid 1", "Avoid 2"],
        if_not_helped="This is a test if_not_helped.",
    )

    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service

    try:
        response = client.post(
            "/recommendations",
            json={
                "age": 4,
                "category": "other",
                "subcategory": "unknown",
                "place": "home",
            },
        )

        mock_ai_service.generate.assert_awaited_once()
    finally:
        app.dependency_overrides.pop(get_ai_service, None)

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
        "/recommendations",
        json={"age": "hello", "situation": "не хочет спать"},
    )

    assert response.status_code == 422


def test_recommendations_endpoint_age_out_of_range():
    """Тестирование эндпоинта /recommendations с возрастом вне допустимого диапазона."""
    client = TestClient(app)

    response = client.post(
        "/recommendations",
        json={"age": 0, "situation": "не хочет спать"},
    )

    assert response.status_code == 422

    response = client.post(
        "/recommendations",
        json={"age": 17, "situation": "не хочет спать"},
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

    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate = AsyncMock(return_value=mock_result)

    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service

    try:
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

        assert mock_ai_service.generate.await_count == 2
    finally:
        app.dependency_overrides.pop(get_ai_service, None)


def test_recommendations_endpoint_ai_error():
    """Тестирование ошибки AI-сервиса."""
    client = TestClient(app)

    request_counts.clear()

    mock_ai_service = MagicMock(spec=AIService)
    mock_ai_service.generate = AsyncMock(
        side_effect=AIServiceError("AI error"),
    )

    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service

    try:
        response = client.post(
            "/recommendations",
            json={
                "age": 4,
                "category": "other",
                "subcategory": "unknown",
                "place": "home",
            },
        )
    finally:
        app.dependency_overrides.pop(get_ai_service, None)

    assert response.status_code == 503