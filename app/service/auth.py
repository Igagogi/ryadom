from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core import security
from app.db.models import User
from app.repository import users


def register_user(db: Session, name: str, age: int, email: str, password: str) -> User:

    user = users.get_user_by_email(db, email)

    if user is not None:
        raise HTTPException(400, "Пользователь с таким email уже существует")

    hashed_password = security.hash_password(password)

    new_user = users.create_user(db, name, age, email, hashed_password)

    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(db: Session, email: str, password: str) -> dict:

    user = users.get_user_by_email(db, email)

    if user is None:
        raise HTTPException(401, "Неверный email или пароль")

    if user.password_hash is None:
        raise HTTPException(401, "Неверный email или пароль")

    if not security.verify_password(password, user.password_hash):
        raise HTTPException(401, "Неверный email или пароль")

    access_token = security.create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
