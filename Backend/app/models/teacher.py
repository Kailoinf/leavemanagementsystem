from sqlmodel import SQLModel, Field


class Teacher(SQLModel, table=True):
    teacher_id: int = Field(primary_key=True)
    teacher_name: str = Field(max_length=8)
    password: str = Field(max_length=60, default=None)
