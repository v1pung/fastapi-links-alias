from pydantic import BaseModel


class RegisterUserRequest(BaseModel):
    username: str
    password: str


class RegisterUserResponse(BaseModel):
    message: str
