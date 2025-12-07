from datetime import datetime
from typing import Union
from pydantic import BaseModel, Field, field_validator


class StudentCreate(BaseModel):
    student_id: int
    name: str = Field(max_length=8)
    password: str = None
    school: str = Field(max_length=8, default=None)
    reviewer_id: int = None
    guarantee_permission: Union[datetime, str]

    @field_validator("guarantee_permission", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v