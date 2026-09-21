from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StoryMood(str, Enum):
    FUNNY = "funny"
    CALM = "calm"
    ADVENTURE = "adventure"


class StoryDuration(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class StoryRequest(BaseModel):
    age: int = Field(ge=1, le=16, description="Возраст ребёнка (от 1 до 16 лет)")
    name: str | None = Field(default=None, description="Имя ребёнка (необязательно)")
    mood: StoryMood = Field(description="Настроение истории")
    character: str | None = Field(default=None, description="Предпочитаемый персонаж истории (необязательно)")
    duration: StoryDuration = Field(description="Продолжительность истории")

class StoryAIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Название истории")
    story: str = Field(description="Текст истории")

class StoryResponse(BaseModel):
    title: str = Field(description="Название истории")
    story: str = Field(description="Текст истории")