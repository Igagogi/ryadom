from openai import AsyncOpenAI
from pydantic import BaseModel

from app.ai.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> str:
        response = await self.client.responses.parse(
            model="gpt-5-mini",
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            text_format=response_model,
        )

        parsed = response.output_parsed

        if parsed is None:
            raise ValueError("OpenAI не вернул структурированный ответ")

        return parsed.model_dump_json()