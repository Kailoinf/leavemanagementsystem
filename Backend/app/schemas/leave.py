from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel, Field, field_validator


class LeaveCreate(BaseModel):
    student_id: Optional[int] = None
    leave_date: Optional[Union[datetime, str]] = None
    class_hours: str = Field(max_length=8, default=None)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: str = Field(max_length=8, default=None)
    remarks: str = Field(max_length=100, default=None)
    materials: str = Field(max_length=100, default=None)
    reviewer_id: Optional[int] = None
    teacher_id: int = None
    audit_remarks: str = Field(max_length=100, default=None)
    audit_time: Optional[Union[datetime, str]] = None
    course_id: int = None
    is_modified: str = Field(max_length=12, default="否")  # 创建时默认为否
    guarantee_student_id: int = None

    @field_validator("leave_date", "audit_time", mode="before")
    @classmethod
    def parse_optional_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v