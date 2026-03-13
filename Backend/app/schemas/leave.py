from datetime import datetime
from typing import Union, Optional
from pydantic import BaseModel, Field, field_validator


class LeaveCreate(BaseModel):
    student_id: Optional[int] = None
    leave_date: Optional[Union[datetime, str]] = None
    leave_hours: Optional[str] = Field(max_length=8, default=None)
    status: str = Field(max_length=8)  # 待审批、已批准、已拒绝、已撤销
    leave_type: Optional[str] = Field(max_length=8, default=None)  # 事假、病假、公假、婚假、丧假
    remarks: Optional[str] = Field(max_length=100, default=None)
    materials: Optional[str] = Field(max_length=100, default=None)
    reviewer_id: Optional[int] = None
    teacher_id: Optional[int] = None
    audit_remarks: Optional[str] = Field(max_length=100, default=None)
    audit_time: Optional[Union[datetime, str]] = None
    course_id: Optional[int] = None
    is_modified: bool = False  # 改为布尔类型，默认 False
    guarantee_student_id: Optional[int] = None

    @field_validator("leave_date", "audit_time", mode="before")
    @classmethod
    def parse_optional_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v
