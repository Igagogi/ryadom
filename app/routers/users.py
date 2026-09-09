from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.users import UserResponse
from app.service.users import get_users

router = APIRouter()

@router.get("/users", response_model=list[UserResponse])
def get_users_endpoint(
    db: Session = Depends(get_db)
):
    return get_users(db)