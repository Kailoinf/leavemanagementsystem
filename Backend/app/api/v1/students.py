from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database.connection import get_session
from app.models import Student
from app.schemas import StudentCreate, PaginatedResponse
from app.services.student import StudentService

router = APIRouter()


@router.get("/students", response_model=PaginatedResponse, summary="分页获取学生列表")
def read_students(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    items, total, total_pages = StudentService.get_students(
        token, page, page_size, session
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/students/count")
def students_count(token: str, session: Session = Depends(get_session)):
    return StudentService.get_students_count(token, session)


@router.get("/students/{student_id}", response_model=Student)
def read_student(token: str, student_id: int, session: Session = Depends(get_session)):
    return StudentService.get_student_by_id(token, student_id, session)


@router.post("/students", response_model=Student, summary="创建学生")
def create_student_endpoint(
    token: str,
    student_data: StudentCreate,
    session: Session = Depends(get_session),
):
    return StudentService.create_student(token, student_data, session)
