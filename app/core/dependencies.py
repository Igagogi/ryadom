import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import JWT_ALGORITHM, JWT_SECRET_KEY
from app.db.database import get_db
from app.repository import users as user_repository

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
        db: Session = Depends(get_db),
    ):

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


def get_optional_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme), 
        db: Session = Depends(get_db),
    ):

    """ Получает текущего аутентифицированного пользователя на основе JWT, если токен предоставлен.
        Если токен не предоставлен, возвращает None."""
    
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None

    user = user_repository.get_user_by_id(db, user_id)

    return user