from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    age: int
    situation: str

class RecommendationResponse(BaseModel):
    recommendation: str

class RecommendationAIResponse(BaseModel):
    steps: list[str]
    phrase: str
    avoid: list[str]
    if_not_helped: str
