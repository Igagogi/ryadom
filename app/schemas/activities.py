from pydantic import BaseModel, ConfigDict, Field


class ActivityRequest(BaseModel):
    age: int = Field(ge=1, le=16, description="Возраст ребёнка в годах (от 1 до 16)")
    time: int = Field(gt=0, le=120, description="Продолжительность активности в минутах (от 1 до 120)")
    place: str = Field(min_length=1, description="Место проведения активности")
    available_items: list[str] = Field(default_factory=list, description="Доступные предметы для активности")

class ActivityResponse(BaseModel):
    title: str = Field(description="Название активности")
    description: str = Field(description="Описание активности")
    steps: list[str] = Field(description="Этапы выполнения активности")
    duration: int = Field(gt=0, description="Продолжительность активности в минутах")

class ActivityAIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Название активности")
    description: str = Field(description="Описание активности")
    steps: list[str] = Field(description="Этапы выполнения активности")
    duration: int = Field(gt=0, description="Продолжительность активности в минутах")