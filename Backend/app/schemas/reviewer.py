from pydantic import BaseModel, Field


class ReviewerCreate(BaseModel):
    reviewer_id: int
    name: str = Field(max_length=8)
    school: str = Field(max_length=8, default=None)
    role: str = Field(max_length=10, default=None)
    password: str = None