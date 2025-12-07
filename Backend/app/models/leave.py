from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Leave(SQLModel, table=True):
    leave_id: int = Field(primary_key=True)
    student_id: int = Field(foreign_key="student.student_id")
    leave_date: datetime
    class_hours: Optional[str] = Field(max_length=8, default=None)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: Optional[str] = Field(max_length=8, default=None)
    remarks: Optional[str] = Field(max_length=100, default=None)
    materials: Optional[str] = Field(max_length=100, default=None)
    reviewer_id: Optional[int] = Field(foreign_key="reviewer.reviewer_id", default=None)
    teacher_id: Optional[int] = Field(foreign_key="teacher.teacher_id", default=None)
    audit_remarks: Optional[str] = Field(max_length=100, default=None)
    audit_time: Optional[datetime] = Field(default=None)
    course_id: Optional[int] = Field(foreign_key="course.course_id", default=None)
    is_modified: Optional[str] = Field(max_length=12, default=None)
    guarantee_student_id: Optional[int] = Field(
        foreign_key="student.student_id", default=None
    )