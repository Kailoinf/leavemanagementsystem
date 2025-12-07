from typing import List
from fastapi import APIRouter, Depends

from app.database.connection import get_session
from app.models import StudentCourse
from app.schemas import StudentCourseCreate, StudentCourseResponse
from app.services.student_course import StudentCourseService

router = APIRouter()


@router.post("/student-courses", response_model=StudentCourse)
def create_student_course_endpoint(
    token: str,
    student_course_data: StudentCourseCreate,
    session=Depends(get_session),
):
    """学生选课"""
    return StudentCourseService.create_student_course(token, student_course_data, session)


@router.get("/student-courses/student/{student_id}", response_model=List[StudentCourseResponse])
def get_student_courses_endpoint(
    token: str,
    student_id: int = None,
    session=Depends(get_session),
):
    """获取学生的选课列表"""
    return StudentCourseService.get_student_courses(token, student_id, session)


@router.get("/student-courses/course/{course_id}", response_model=List[StudentCourseResponse])
def get_course_students_endpoint(
    token: str,
    course_id: int,
    session=Depends(get_session),
):
    """获取课程的学生列表"""
    return StudentCourseService.get_course_students(token, course_id, session)


@router.get("/student-courses/teacher/{teacher_id}/similar-courses/{course_id}", response_model=List[StudentCourseResponse])
def get_similar_course_students_endpoint(
    token: str,
    teacher_id: int,
    course_id: int,
    session=Depends(get_session),
):
    """获取同一教师下相似课程的学生列表（防止请错课程）"""
    return StudentCourseService.get_similar_course_students(token, teacher_id, course_id, session)