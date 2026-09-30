import json
import logging

from pydantic import BaseModel, ValidationError

from app.ai.base import LLMProvider

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Ошибка при работе с AI-сервисом."""


class AIService:

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> BaseModel:

        try:
            raw_response = await self.provider.generate(
                system_prompt,
                user_prompt,
                response_model,
            )

            logger.warning(
                "AI raw response: %r",
                raw_response,
            )

            data = json.loads(raw_response)

            return response_model.model_validate(data)

        except (json.JSONDecodeError, ValidationError) as exc:
            logger.exception(
                "AI вернул некорректный ответ"
            )

            raise AIServiceError(
                "AI вернул некорректный ответ"
            ) from exc