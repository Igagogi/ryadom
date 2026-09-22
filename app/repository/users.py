from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


def create_user(
    db: Session, name: str, age: int, email: str, password_hash: str
) -> User:
    """Создать нового пользователя в базе данных."""
    new_user = User(name=name, age=age, email=email, password_hash=password_hash)
    db.add(new_user)
    return new_user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Получить пользователя по его ID."""
    result = db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


def update_user(
    db: Session, user_id: int, name: str | None = None, age: int | None = None
) -> User | None:
    """Обновить данные пользователя по его ID."""
    user = get_user_by_id(db, user_id)
    if user is None:
        return None

    if name is not None:
        user.name = name

    if age is not None:
        user.age = age

    return user


def delete_user(db: Session, user_id: int) -> User | None:
    """Удалить пользователя по его ID."""
    user = get_user_by_id(db, user_id)

    if user is None:
        return None

    db.delete(user)

    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Получить пользователя по его email."""
    result = db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
