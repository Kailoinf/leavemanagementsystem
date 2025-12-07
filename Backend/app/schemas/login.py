from pydantic import BaseModel


class UserLogin(BaseModel):
    role: str
    id: int
    password: str
    token: str