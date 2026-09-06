from pydantic import BaseModel, ConfigDict, Field


class RecommendationRequest(BaseModel):
    age: int = Field(ge=1, le=16, description="Возраст ребёнка (от 1 до 16 лет)")
    situation: str = Field(min_length=3, description="Описание ситуации, с которой сталкивается ребёнок")

class RecommendationResponse(BaseModel):
    steps: list[str]
    phrase: str
    avoid: list[str]
    if_not_helped: str

class RecommendationAIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    steps: list[str]
    phrase: str
    avoid: list[str]
    if_not_helped: str
