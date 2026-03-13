from sqlmodel import SQLModel, Field
from typing import Optional


class Reviewer(SQLModel, table=True):
    """审核员表 - 符合第三范式"""
    reviewer_id: int = Field(primary_key=True)
    reviewer_name: str = Field(max_length=8)
    school_id: Optional[int] = Field(foreign_key="school.school_id", default=None)  # 外键引用 school 表
    role_id: Optional[int] = Field(foreign_key="role.role_id", default=None)  # 外键引用 role 表
    password: Optional[str] = Field(max_length=60, default=None)
