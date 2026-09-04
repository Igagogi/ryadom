from pydantic import BaseModel, ConfigDict


class RecommendationRequest(BaseModel):
    age: int
    situation: str

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
