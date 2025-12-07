from pydantic import BaseModel, Field


class TeacherCreate(BaseModel):
    teacher_id: int
    name: str = Field(max_length=8)
    password: str = None