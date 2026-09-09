from unittest.mock import Mock, patch

import pytest
from groq import APITimeoutError

from app.service.ai import AIServiceError, generate_ai_recommendation


@pytest.mark.anyio
async def test_generate_ai_recommendation_timeout():
    """Тестирование генерации рекомендации с использованием AI при тайм-ауте."""
    with patch("app.service.ai.client.chat.completions.create",
               side_effect=APITimeoutError("timeout")
               ):
          with pytest.raises(AIServiceError):
                 await generate_ai_recommendation(
                       4,
                       "ребёнок не хочет идти спать"
                       )

@pytest.mark.anyio
async def test_generate_ai_recommendation_invalid_json():
    """Тестирование генерации рекомендации с использованием AI при получении некорректного JSON."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "это не JSON"

    with patch(
        "app.service.ai.client.chat.completions.create",
        return_value=mock_response
    ), pytest.raises(AIServiceError):
        await generate_ai_recommendation(
            4,
            "ребёнок не хочет идти спать"
        )

@pytest.mark.anyio
async def test_generate_ai_recommendation_invalid_schema():
    """Тестирование генерации рекомендации с использованием AI при получении JSON, не соответствующего схеме."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = """
    {
        "steps": ["Успокойте ребёнка"],
        "phrase": "Давай попробуем вместе",
        "avoid": ["Не кричать"]
    }
    """

    with patch(
        "app.service.ai.client.chat.completions.create",
        return_value=mock_response
    ), pytest.raises(AIServiceError):
        await generate_ai_recommendation(
            4,
            "ребёнок не хочет идти спать"
        )
