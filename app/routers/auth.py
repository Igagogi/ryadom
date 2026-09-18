from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.service import auth as auth_service

router = APIRouter()


@router.post("/auth/register", response_model=RegisterResponse)
def register_user(
    user: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Регистрация пользователя."""
    return auth_service.register_user(
        db,
        user.name,
        user.age,
        user.email,
        user.password,
    )


@router.post("/auth/login", response_model=LoginResponse)
def login_user(
    user: LoginRequest,
    db: Session = Depends(get_db),
):
    """Авторизация пользователя."""
    return auth_service.login_user(
        db,
        user.email,
        user.password,
    )