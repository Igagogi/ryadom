from app.schemas.recommendations import RecommendationAIResponse


def generate_ai_recommendation(age: int, situation: str) -> RecommendationAIResponse:
    steps = [
        "Шаг 1: Успокойте ребенка",
        "Шаг 2: Обеспечьте комфортную обстановку",
        "Шаг 3: Предложите игрушку или занятие"
    ]
    phrase = f"Рекомендации для возраста {age} и ситуации '{situation}'"
    avoid = ["Не кричите на ребенка", "Не оставляйте его одного"]
    if_not_helped = "Если рекомендации не помогли, обратитесь к специалисту."

    return RecommendationAIResponse(
        steps=steps,
        phrase=phrase,
        avoid=avoid,
        if_not_helped=if_not_helped
    )