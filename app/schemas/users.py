from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    age: int

class UserUpdate(BaseModel):
    name: str | None = None
    age: int | None = None

