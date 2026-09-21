import json
import os

from dotenv import load_dotenv
from groq import (
    APIConnectionError,
    APITimeoutError,
    AsyncGroq,
    BadRequestError,
    InternalServerError,
    RateLimitError,
)
from pydantic import ValidationError

from app.schemas.activities import ActivityAIResponse
from app.schemas.recommendations import RecommendationAIResponse
from app.schemas.story import StoryAIResponse, StoryDuration, StoryMood


class AIServiceError(Exception):
    pass

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = AsyncGroq(api_key=api_key)

RECOMMENDATIONS_SYSTEM_PROMPT = (
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

ACTIVITY_SYSTEM_PROMPT = """
Ты — помощник для родителей детей.

Твоя задача — предложить ОДНО конкретное занятие,
которое родитель может начать с ребёнком прямо сейчас.

Учитывай:
- возраст ребёнка;
- доступное время;
- место проведения;
- доступные предметы и материалы.

Правила:
- предлагай только одно занятие;
- занятие должно соответствовать возрасту ребёнка;
- занятие не должно требовать больше времени,
  чем доступно пользователю;
- если указаны доступные предметы, используй их;
- не требуй материалов, которых нет в списке;
- если список пуст, предложи занятие без специальных материалов;
- описание должно быть коротким и понятным;
- шаги должны быть последовательными и практичными;
- не предлагай опасные действия;
- duration не должен превышать доступное время;
- верни только данные в соответствии с JSON Schema;
- Если место связано с транспортом, не предлагай действия,
которые могут отвлечь водителя или требуют вставать/перемещаться
во время движения;
- Учитывай контекст места: если ребёнок уже находится в указанном месте,
не предлагай действия, предполагающие сначала добраться туда или подготовить это место;
- Название должно быть естественным, коротким и грамматически корректным на русском языке.
"""

STORY_SYSTEM_PROMPT = """
Ты создаёшь короткие детские истории.

Правила:
- учитывай возраст ребёнка;
- используй имя ребёнка, если оно указано;
- учитывай настроение истории;
- используй указанного персонажа, если он задан;
- история должна соответствовать возрасту ребёнка;
- история должна быть доброй и безопасной;
- не используй страшные сцены, насилие и опасные инструкции;
- учитывай выбранную продолжительность;
- верни только JSON согласно заданной схеме;
- short — примерно 3 минуты;
- medium — примерно 5 минут;
- long — примерно 10 минут.
"""

async def generate_ai_recommendation(
    age: int, 
    situation: str
) -> RecommendationAIResponse:

    schema = RecommendationAIResponse.model_json_schema()

    try: 
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": RECOMMENDATIONS_SYSTEM_PROMPT},
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


async def generate_ai_activity(
    age: int,
    time: int,
    place: str,
    available_items: list[str],
    correction: str | None = None,
) -> ActivityAIResponse:

    schema = ActivityAIResponse.model_json_schema()

    messages = [
        {"role": "system", "content": ACTIVITY_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Возраст ребёнка: {age}. "
                f"Доступное время: {time} минут. "
                f"Место проведения: {place}. "
                f"Доступные предметы: "
                f"{', '.join(available_items) if available_items else 'нет'}."
            ),
        },
    ]

    if correction:
        messages.append(
            {
                "role": "user",
                "content": correction,
            }
        )

    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "activity",
                    "strict": True,
                    "schema": schema
                }
            }
        )
    except (
        APIConnectionError,
        APITimeoutError,
        InternalServerError,
        RateLimitError,
        BadRequestError,
    ) as e:
        raise AIServiceError(
            "Ошибка при генерации активности AI:"
        ) from e

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        result = ActivityAIResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise AIServiceError(
            "AI-сервис вернул некорректный ответ"
        ) from e

    return result


async def generate_ai_story(
    age: int,
    name: str | None,
    mood: StoryMood,
    character: str | None,
    duration: StoryDuration
) -> StoryAIResponse:
    
    schema = StoryAIResponse.model_json_schema()

    messages = [
        {"role": "system", "content": STORY_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Возраст ребёнка: {age}. "
                f"Имя ребёнка: {name or 'не указано'}. "
                f"Настроение истории: {mood.value}. "
                f"Предпочитаемый персонаж: {character or 'не указан'}. "
                f"Продолжительность истории: {duration.value}. "
            )
        }
    ]

    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "story",
                    "strict": True,
                    "schema": schema
                }
            }
        )
    except (
        APIConnectionError,
        APITimeoutError,
        InternalServerError,
        RateLimitError,
        BadRequestError
    ) as e:
        
        print("AI ERROR:", type(e).__name__, e)
        
        raise AIServiceError(
            "Ошибка при генерации истории AI:"
        ) from e

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        result = StoryAIResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise AIServiceError(
            "AI-сервис вернул некорректный ответ"
        ) from e

    return result