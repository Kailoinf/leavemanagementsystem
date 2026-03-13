from pydantic import BaseModel, Field


class AdminCreate(BaseModel):
    name: str = Field(max_length=8)
    password: str