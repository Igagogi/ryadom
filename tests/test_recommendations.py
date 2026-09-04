from unittest.mock import Mock, patch

from app.schemas.recommendations import RecommendationAIResponse
from app.service.recommendations import generate_recommendation


def test_generate_recommendation_with_scenario():
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
        result = generate_recommendation(age, situation)
        mock_ai.generate_ai_recommendation.assert_not_called()

    assert result is not None
    assert result.phrase == "Сейчас время готовиться ко сну. Давай вместе закончим наш день."

def test_generate_recommendation_with_ai():
    """Тестирование генерации рекомендации с использованием AI."""
    age = 2
    situation = "ребёнок боится идти в детский сад"

    mock_ai = Mock()
    
    mock_ai.generate_ai_recommendation.return_value = RecommendationAIResponse(
        steps=["Step 1", "Step 2"],
        phrase="This is a test phrase.",
        avoid=["Avoid 1", "Avoid 2"],
        if_not_helped="This is a test if_not_helped."
        )

    with patch("app.service.recommendations.ai.generate_ai_recommendation", new=mock_ai.generate_ai_recommendation):
        result = generate_recommendation(age, situation)
        mock_ai.generate_ai_recommendation.assert_called_once_with(age, situation)

    assert result is not None
    assert result.phrase == "This is a test phrase."