from app.schemas.activities import ActivityResponse

ACTIVITY_SCENARIOS = [
    {
        "age_min": 2,
        "age_max": 3,
        "place": "дом",
        "required_items": [],
        "title": "Охота за цветами",
        "description": "Найдите дома предметы разных цветов и соберите их в небольшие группы.",
        "steps": [
            "Выберите один цвет, например красный.",
            "Попросите ребёнка найти в комнате предметы этого цвета.",
            "Соберите найденные предметы вместе.",
            "Выберите следующий цвет и повторите игру."
        ],
        "duration": 10,
    },
    {
        "age_min": 3,
        "age_max": 5,
        "place": "дом",
        "required_items": ["бумага", "карандаши"],
        "title": "Нарисуй историю",
        "description": "Придумайте короткую историю и нарисуйте её по шагам.",
        "steps": [
            "Придумайте героя истории.",
            "Нарисуйте героя на бумаге.",
            "Придумайте, что с ним произошло.",
            "Нарисуйте ещё один или два момента истории.",
            "Расскажите историю друг другу."
        ],
        "duration": 15,
    }
]


def find_activity_scenario(
    age: int,
    time: int,
    place: str,
    available_items: list[str],
) -> ActivityResponse | None:
    for scenario in ACTIVITY_SCENARIOS:
        if (
            scenario["age_min"] <= age <= scenario["age_max"]
            and scenario["place"] == place.lower()
            and scenario["duration"] <= time
            and all(
                item in available_items
                for item in scenario["required_items"]
            )
        ):
            return ActivityResponse(
                title=scenario["title"],
                description=scenario["description"],
                steps=scenario["steps"],
                duration=scenario["duration"],
            )

    return None