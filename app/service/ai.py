import json
import os

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APITimeoutError,
    AsyncGroq,
    InternalServerError,
    RateLimitError,
)
from pydantic import ValidationError

from app.schemas.recommendations import RecommendationAIResponse


class AIServiceError(Exception):
    pass

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = AsyncGroq(api_key=api_key)

SYSTEM_PROMPT = (
    "Ты — AI-помощник для родителей детей 2–6 лет. "
    "Твоя задача — давать короткие, практичные и понятные рекомендации "
    "для повседневных ситуаций с ребёнком. "
    "Сформируй рекомендацию, которая поможет родителю понять, что сделать прямо сейчас. "
    "Пиши простым языком, кратко и без осуждения родителя или ребёнка. "
    "Не ставь диагнозы. "
    "Не выдавай себя за врача. "
    "Не выдавай медицинские рекомендации как замену обращению к медицинскому специалисту. "
    "Не предлагай потенциально опасные действия. "
    "Всегда отвечай на русском языке, независимо от языка входного запроса. "
    "Всегда заполнять все четыре поля: steps, phrase, avoid, if_not_helped. "
    "Ни одно поле не должно отсутствовать или быть пустым. "
)

async def generate_ai_recommendation(age: int, situation: str) -> RecommendationAIResponse:

    schema = RecommendationAIResponse.model_json_schema()

    try: 
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Возраст ребёнка: {age}. Ситуация: {situation}. "
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "recommendation",
                    "strict": True,
                    "schema": schema
                    }
            }
        )
    except (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError) as e:
        raise AIServiceError("Ошибка при генерации рекомендации AI:") from e
 
    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        result = RecommendationAIResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise AIServiceError(
            "AI-сервис вернул некорректный ответ"
        ) from e

    return result