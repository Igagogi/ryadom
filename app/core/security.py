import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY не установлен в переменных окружения.")

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Хэширует пароль с использованием безопасного алгоритма."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и его хэша."""
    return password_hash.verify(password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создает JWT токен с указанными данными и временем истечения."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
