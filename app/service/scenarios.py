from app.schemas.scenarios import Scenario


def find_scenario(age: int, situation: str) -> Scenario | None:
    
    for scenario in SCENARIOS.values():
        if scenario.min_age <= age <= scenario.max_age:
            for keyword in scenario.keywords:
                if keyword in situation.lower():
                    return scenario
                
    return None


SCENARIOS = {
    "bedtime": Scenario(
        min_age=3,
        max_age=5,
        keywords=[
            "не хочет спать",
            "не хочет ложиться",
            "не хочет идти спать",
            "отказывается спать",
        ],
        steps=[
            "Приглушите свет",
            "Уберите активные игры",
            "Расскажите короткую сказку",
        ],
        phrase="Сейчас время готовиться ко сну. Давай вместе закончим наш день.",
        avoid=[
            "Включать телевизор",
            "Устраивать активные игры",
            "Угрожать наказанием",
        ],
        if_not_helped="Попробуйте сделать одинаковый спокойный ритуал перед сном каждый вечер.",
        )
}