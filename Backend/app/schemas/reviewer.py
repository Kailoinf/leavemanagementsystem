from typing import Optional
from pydantic import BaseModel, Field


class ReviewerCreate(BaseModel):
    reviewer_id: int
    reviewer_name: str = Field(max_length=8)  # 修复字段名匹配模型
    school_id: Optional[int] = None  # 改为 school_id 外键
    role_id: Optional[int] = None  # 改为 role_id 外键
    password: Optional[str] = None