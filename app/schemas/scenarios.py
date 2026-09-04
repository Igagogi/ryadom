from pydantic import BaseModel


class Scenario(BaseModel):
    min_age: int
    max_age: int
    keywords: list[str]
    steps: list[str]
    phrase: str
    avoid: list[str]
    if_not_helped: str