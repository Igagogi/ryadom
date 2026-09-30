from app.ai.factory import create_provider
from app.ai.service import AIService


def get_ai_service() -> AIService:
    provider = create_provider()

    return AIService(provider)