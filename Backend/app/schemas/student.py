from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel, Field, field_validator


class StudentCreate(BaseModel):
    student_id: int
    student_name: str = Field(max_length=8)  # 修复字段名匹配模型
    password: Optional[str] = None
    school_id: Optional[int] = None  # 改为 school_id 外键
    reviewer_id: Optional[int] = None
    guarantee_permission: Optional[Union[datetime, str]] = None

    @field_validator("guarantee_permission", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v