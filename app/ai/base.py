from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
    ) -> str:
        pass