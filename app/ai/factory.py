import os

from dotenv import load_dotenv

from app.ai.base import LLMProvider
from app.ai.groq_provider import GroqProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.yandex_provider import YandexProvider

load_dotenv()


def create_provider() -> LLMProvider:
    provider_name = os.getenv("AI_PROVIDER")

    if provider_name == "yandex":
        api_key = os.getenv("YANDEX_API_KEY")
        folder_id = os.getenv("YANDEX_FOLDER_ID")

        if not api_key or not folder_id:
            raise ValueError(
                "YANDEX_API_KEY и YANDEX_FOLDER_ID должны быть указаны"
            )

        return YandexProvider(
            api_key=api_key,
            folder_id=folder_id,
        )

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY должен быть указан"
            )

        return OpenAIProvider(
            api_key=api_key,
        )

    if provider_name == "groq":
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY должен быть указан"
            )

        return GroqProvider(
            api_key=api_key,
        )


    raise ValueError(
        f"Неизвестный AI_PROVIDER: {provider_name}"
    )