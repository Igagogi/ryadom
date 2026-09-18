from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserResponse, UserUpdate
from app.service import users as user_service

router = APIRouter()

@router.get("/users", response_model=list[UserResponse])
def get_users_endpoint(db: Session = Depends(get_db)):
    """Получить всех пользователей из базы данных."""
    return user_service.get_users(db)

@router.get("/users/me", response_model=UserResponse)
def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем аутентифицированном пользователе."""
    return current_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id_endpoint(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получить пользователя по его ID."""
    return user_service.get_user_by_id(db, user_id, current_user)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_endpoint(user_id: int, user: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обновить данные пользователя по его ID."""
    return user_service.update_user(db, user_id, current_user, user.name, user.age)

@router.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Удалить пользователя по его ID."""
    user_service.delete_user(db, user_id, current_user)
    return {"message": "Пользователь удалён"}   