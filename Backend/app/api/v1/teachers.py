from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database.connection import get_session
from app.models import Teacher
from app.schemas import TeacherCreate, PaginatedResponse
from app.services.teacher import TeacherService

router = APIRouter()


@router.get("/teachers", response_model=PaginatedResponse)
def read_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    teachers, total, total_pages = TeacherService.get_teachers(page, page_size, session)
    return PaginatedResponse(
        items=teachers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/teachers/count")
def teachers_count(session: Session = Depends(get_session)):
    return TeacherService.get_teachers_count(session)


@router.get("/teachers/{teacher_id}", response_model=Teacher)
def read_teacher(teacher_id: int, session: Session = Depends(get_session)):
    return TeacherService.get_teacher_by_id(teacher_id, session)


@router.post("/teachers", response_model=Teacher, summary="创建教师")
def create_teacher_endpoint(
    teacher_data: TeacherCreate,
    session: Session = Depends(get_session),
):
    return TeacherService.create_teacher(teacher_data, session)