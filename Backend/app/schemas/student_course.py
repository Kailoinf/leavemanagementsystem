from typing import List, Optional
from pydantic import BaseModel, Field


class StudentCourseCreate(BaseModel):
    student_id: int
    course_id: int
    enrollment_date: Optional[str] = Field(default=None, max_length=20)
    status: str = Field(default="已选课", max_length=20)


class StudentCourseResponse(BaseModel):
    student_id: int
    course_id: int
    enrollment_date: Optional[str] = None
    status: str
    student_name: Optional[str] = None  # 学生姓名
    course_name: Optional[str] = None  # 课程名称
    teacher_name: Optional[str] = None  # 教师姓名


class StudentCourse(BaseModel):
    pass  # 用于查询所有选课记录