from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class LeaveStatus(str, Enum):
    """请假状态枚举"""
    PENDING = "待审批"
    APPROVED = "已批准"
    REJECTED = "已拒绝"
    CANCELLED = "已撤销"


class LeaveType(str, Enum):
    """请假类型枚举"""
    PERSONAL = "事假"
    SICK = "病假"
    PUBLIC = "公假"
    MARRIAGE = "婚假"
    BEREAVEMENT = "丧假"


class Leave(SQLModel, table=True):
    """请假表 - 符合第三范式"""
    leave_id: int = Field(primary_key=True)
    student_id: int = Field(foreign_key="student.student_id")
    leave_date: datetime
    leave_hours: Optional[str] = Field(max_length=8, default=None)
    status: str = Field(max_length=8)  # LeaveStatus 枚举值
    leave_type: Optional[str] = Field(max_length=8, default=None)  # LeaveType 枚举值
    remarks: Optional[str] = Field(max_length=100, default=None)
    materials: Optional[str] = Field(max_length=100, default=None)
    reviewer_id: Optional[int] = Field(foreign_key="reviewer.reviewer_id", default=None)
    teacher_id: Optional[int] = Field(foreign_key="teacher.teacher_id", default=None)
    audit_remarks: Optional[str] = Field(max_length=100, default=None)
    audit_time: Optional[datetime] = Field(default=None)
    course_id: Optional[int] = Field(foreign_key="course.course_id", default=None)
    is_modified: bool = Field(default=False)  # 改为布尔类型
    guarantee_student_id: Optional[int] = Field(
        foreign_key="student.student_id", default=None
    )