from sqlmodel import SQLModel, Field
from datetime import datetime


class Leave(SQLModel, table=True):
    leave_id: int = Field(primary_key=True)
    student_id: int = Field(foreign_key="student.student_id")
    leave_date: datetime
    class_hours: str = Field(max_length=8, default=None)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: str = Field(max_length=8, default=None)
    remarks: str = Field(max_length=100, default=None)
    materials: str = Field(max_length=100, default=None)
    reviewer_id: int = Field(foreign_key="reviewer.reviewer_id", default=None)
    teacher_id: int = Field(foreign_key="teacher.teacher_id", default=None)
    audit_remarks: str = Field(max_length=100, default=None)
    audit_time: datetime = None
    course_id: int = Field(foreign_key="course.course_id", default=None)
    is_modified: str = Field(max_length=12, default=None)
    guarantee_student_id: int = Field(
        foreign_key="student.student_id", default=None
    )