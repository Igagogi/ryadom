from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Scenario


def get_scenario(
    db: Session,
    category: str,
    subcategory: str,
    age: int,
    place: str | None = None,
) -> Scenario | None:

    query = select(Scenario).where(
        Scenario.category == category,
        Scenario.subcategory == subcategory,
        Scenario.age_min <= age,
        Scenario.age_max >= age,
        Scenario.is_active.is_(True),
    )

    if place is not None:
        exact_query = query.where(Scenario.place == place)
        scenario = db.scalar(exact_query)

        if scenario is not None:
            return scenario

    universal_query = query.where(Scenario.place.is_(None))

    return db.scalar(universal_query)