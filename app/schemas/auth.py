from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    age: int
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str