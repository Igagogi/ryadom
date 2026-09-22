from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    email: Mapped[str | None]
    password_hash: Mapped[str | None]

class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)

    category: Mapped[str]
    subcategory: Mapped[str]

    age_min: Mapped[int]
    age_max: Mapped[int]

    place: Mapped[str | None]

    title: Mapped[str]
    steps: Mapped[list[str]] = mapped_column(JSON)

    phrase: Mapped[str | None]
    avoid: Mapped[list[str] | None] = mapped_column(JSON)
    if_not_helped: Mapped[str | None]

    is_active: Mapped[bool] = mapped_column(default=True)