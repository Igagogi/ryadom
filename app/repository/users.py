from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


def get_all_users(db: Session) -> list[User]:
    result = db.execute(select(User))
    return result.scalars().all()