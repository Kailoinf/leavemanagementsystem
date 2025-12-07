from pydantic import BaseModel, Field


class AdminCreate(BaseModel):
    admin_id: int
    name: str = Field(max_length=8)
    password: str