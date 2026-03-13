from sqlmodel import SQLModel, Field


class StudentCourse(SQLModel, table=True):
    """学生选课表"""
    student_id: int = Field(foreign_key="student.student_id", primary_key=True)
    course_id: int = Field(foreign_key="course.course_id", primary_key=True)
    enrollment_date: str = Field(max_length=20, default=None)  # 选课时间
    status: str = Field(max_length=20, default="已选课")  # 选课状态：已选课、已退课等