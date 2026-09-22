from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import User
from app.repository import users as user_repository


def get_user_by_id(db: Session, user_id: int, current_user: User) -> User:
    """Получить пользователя по его ID."""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещён",
        )

    user = user_repository.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


def update_user(
    db: Session,
    user_id: int,
    current_user: User,
    name: str | None = None,
    age: int | None = None,
) -> User:
    """Обновить данные пользователя по его ID."""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещён",
        )

    user = user_repository.update_user(db, user_id, name, age)

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user: User) -> User:
    """Удалить пользователя по его ID."""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещён",
        )

    user = user_repository.delete_user(db, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.commit()
    return user
