from sqlalchemy.orm import Session

from app.db.models import User
from app.repository.users import get_all_users


def get_users(db: Session) -> list[User]:
    return get_all_users(db)