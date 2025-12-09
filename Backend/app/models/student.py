from sqlmodel import SQLModel, Field
from datetime import datetime


class Student(SQLModel, table=True):
    student_id: int = Field(primary_key=True)
    student_name: str = Field(max_length=8)
    password: str = Field(max_length=60, default=None)
    school: str = Field(max_length=8, default=None)
    reviewer_id: int = Field(foreign_key="reviewer.reviewer_id", default=None)
    guarantee_permission: datetime
