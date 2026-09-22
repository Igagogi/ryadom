from pydantic import BaseModel, ConfigDict, Field


class RecommendationRequest(BaseModel):
    age: int = Field(
        ge=1,
        le=16,
        description="Возраст ребёнка (от 1 до 16 лет)",
    )
    category: str = Field(
        min_length=1,
        description="Основная категория ситуации",
    )
    subcategory: str = Field(
        min_length=1,
        description="Подкатегория ситуации",
    )
    place: str | None = Field(
        default=None,
        description="Место, где происходит ситуация",
    )


class RecommendationResponse(BaseModel):
    title: str
    steps: list[str]
    phrase: str
    avoid: list[str]
    if_not_helped: str


class RecommendationAIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    steps: list[str]
    phrase: str
    avoid: list[str]
    if_not_helped: str
