import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import JWT_ALGORITHM, JWT_SECRET_KEY
from app.db.database import get_db
from app.repository import users as user_repository

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db),):
    """Получает текущего аутентифицированного пользователя на основе JWT."""

    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM],)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Неверный токен",)

    user = user_repository.get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден",)

    return user