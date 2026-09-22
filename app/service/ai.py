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

from app.constants.scenarios import (
    CATEGORY_LABELS,
    PLACE_LABELS,
    SUBCATEGORY_LABELS,
)
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

RECOMMENDATIONS_SYSTEM_PROMPT = """
Ты — AI-помощник для родителей детей 2–6 лет.

Задача:
Давать короткие, практичные и понятные рекомендации для повседневных ситуаций
с ребёнком, чтобы родитель понимал, что сделать прямо сейчас.

Учитывай:
- возраст ребёнка;
- категорию ситуации;
- подкатегорию ситуации;
- место, если оно указано.

Правила:
- пиши простым и спокойным языком;
- будь кратким и конкретным;
- не осуждай родителя или ребёнка;
- не ставь диагнозы;
- не выдавай себя за врача;
- не заменяй медицинского специалиста;
- не предлагай потенциально опасные действия;
- учитывай возраст ребёнка;
- не придумывай детали ситуации, которых нет во входных данных;
- всегда отвечай на русском языке;
- все пять полей должны быть заполнены:
  title, steps, phrase, avoid, if_not_helped;
- ни одно поле не должно быть пустым;
- title должен быть коротким и понятным названием рекомендации;
- steps должны содержать последовательные практические действия;
- phrase должна содержать готовую фразу, которую родитель может сказать ребёнку;
- avoid должна содержать конкретные действия, которых лучше избегать;
- if_not_helped должна содержать следующий шаг, если первоначальная рекомендация не помогла.
- рекомендации должны быть реалистичными для указанного места;
- не предлагай действия, которые физически или практически
  невозможно выполнить в указанном месте;
- не придумывай предметы, которых нет во входных данных;
- если ситуация обычно требует другого места, сначала предложи
  безопасный способ справиться с ней в текущем месте или спокойно
  перейти в подходящее место;
- не предлагай ребёнку спать, ложиться или устраивать место для сна
  в магазине, на улице или в других неподходящих местах;
- не придумывай несуществующие предметы, действия или условия;
- если информации недостаточно, дай безопасную общую рекомендацию,
  а не выдумывай детали.

Формат ответа:
Верни только данные в соответствии с JSON Schema.
"""


ACTIVITY_SYSTEM_PROMPT = """
Ты — AI-помощник для родителей детей.

Задача:
Предложить одно конкретное занятие, которое родитель может начать
с ребёнком прямо сейчас.

Учитывай:
- возраст ребёнка;
- доступное время;
- место проведения;
- доступные предметы и материалы.

Правила:
- предлагай только одно занятие;
- учитывай возраст ребёнка;
- занятие не должно требовать больше времени, чем доступно пользователю;
- если указаны доступные предметы, используй их;
- не требуй материалов, которых нет в списке;
- если список предметов пуст, предложи занятие без специальных материалов;
- учитывай контекст места;
- если ребёнок уже находится в указанном месте, не предлагай сначала добираться туда;
- описание должно быть коротким и понятным;
- шаги должны быть последовательными и практичными;
- не предлагай опасные действия;
- duration не должен превышать доступное пользователю время;
- если место связано с транспортом, не предлагай действия,
  которые могут отвлечь водителя или требуют вставать или перемещаться
  во время движения;
- title должен быть коротким, естественным и грамматически корректным;
- всегда отвечай на русском языке;
- не придумывай доступные предметы или условия, которых нет во входных данных.

Формат ответа:
Верни только данные в соответствии с JSON Schema.
"""


STORY_SYSTEM_PROMPT = """
Ты — AI-помощник для родителей детей.

Задача:
Создать короткую добрую историю, подходящую для ребёнка указанного возраста.

Учитывай:
- возраст ребёнка;
- имя ребёнка, если оно указано;
- настроение истории;
- предпочтительного персонажа, если он указан;
- выбранную продолжительность.

Правила:
- история должна соответствовать возрасту ребёнка;
- используй имя ребёнка, если оно указано;
- используй указанного персонажа, если он задан;
- учитывай выбранное настроение;
- учитывай выбранную продолжительность;
- история должна быть доброй и безопасной;
- не используй страшные сцены;
- не используй насилие;
- не предлагай опасные действия;
- не добавляй детали, противоречащие входным данным;
- всегда отвечай на русском языке;
- title должен быть коротким и понятным;
- story должна быть цельной и подходящей для чтения ребёнку.

Продолжительность:
- short — примерно 3 минуты;
- medium — примерно 5 минут;
- long — примерно 10 минут.

Формат ответа:
Верни только данные в соответствии с JSON Schema.
"""


async def generate_ai_recommendation(
    age: int,
    category: str,
    subcategory: str,
    place: str | None,
) -> RecommendationAIResponse:

    category_text = CATEGORY_LABELS.get(category, category)
    subcategory_text = SUBCATEGORY_LABELS.get(subcategory, subcategory)
    place_text = PLACE_LABELS.get(place, place or "место не указано")

    schema = RecommendationAIResponse.model_json_schema()

    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": RECOMMENDATIONS_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Возраст ребёнка: {age}. "
                        f"Категория ситуации: {category_text}. "
                        f"Подкатегория ситуации: {subcategory_text}. "
                        f"Место: {place_text}."
                    ),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "recommendation",
                    "strict": True,
                    "schema": schema,
                },
            },
        )
    except (
        APIConnectionError,
        APITimeoutError,
        InternalServerError,
        RateLimitError,
        BadRequestError,
    ) as e:
        raise AIServiceError("Ошибка при генерации рекомендации AI") from e

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        result = RecommendationAIResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise AIServiceError("AI-сервис вернул некорректный ответ") from e

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
                "json_schema": {"name": "activity", "strict": True, "schema": schema},
            },
        )
    except (
        APIConnectionError,
        APITimeoutError,
        InternalServerError,
        RateLimitError,
        BadRequestError,
    ) as e:
        raise AIServiceError("Ошибка при генерации активности AI") from e

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        result = ActivityAIResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise AIServiceError("AI-сервис вернул некорректный ответ") from e

    return result


async def generate_ai_story(
    age: int,
    name: str | None,
    mood: StoryMood,
    character: str | None,
    duration: StoryDuration,
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
            ),
        },
    ]

    try:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "story", "strict": True, "schema": schema},
            },
        )
    except (
        APIConnectionError,
        APITimeoutError,
        InternalServerError,
        RateLimitError,
        BadRequestError,
    ) as e:

        raise AIServiceError("Ошибка при генерации истории AI") from e

    try:
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        result = StoryAIResponse(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        raise AIServiceError("AI-сервис вернул некорректный ответ") from e

    return result
