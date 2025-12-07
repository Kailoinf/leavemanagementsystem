from sqlmodel import SQLModel, Field


class Course(SQLModel, table=True):
    course_id: int = Field(primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.teacher_id")
    course_name: str = Field(max_length=12)
    class_hours: str = Field(max_length=8, default=None)