import asyncio

from pydantic import BaseModel
from yandex_ai_studio_sdk import AIStudio

from app.ai.base import LLMProvider


class YandexProvider(LLMProvider):

    def __init__(self, api_key: str, folder_id: str):
        self.api_key = api_key
        self.folder_id = folder_id

        self.sdk = AIStudio(
            folder_id=folder_id,
            auth=api_key,
        )

        self.model = self.sdk.models.completions(
            "yandexgpt-lite"
        ).configure(
            temperature=0.2,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> str:

        messages = [
            {
                "role": "system",
                "text": system_prompt,
            },
            {
                "role": "user",
                "text": user_prompt,
            },
        ]

        configured_model = self.model.configure(
            response_format=response_model,
        )

        result = await asyncio.to_thread(
            configured_model.run,
            messages,
        )

        return result.alternatives[0].text