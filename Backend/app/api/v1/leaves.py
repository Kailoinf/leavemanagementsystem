from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database.connection import get_session
from app.models import Leave
from app.schemas import LeaveCreate, PaginatedResponse
from app.services.leave import LeaveService

router = APIRouter()


@router.get("/leaves", response_model=PaginatedResponse)
def read_leaves(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    items, total, total_pages = LeaveService.get_leaves(token, page, page_size, session)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/leaves/count")
def leaves_count(token: str, session: Session = Depends(get_session)):
    return LeaveService.get_leaves_count(token, session)


@router.post("/leaves", response_model=Leave)
def create_leave_endpoint(
    token: str,
    leave_data: LeaveCreate,
    session: Session = Depends(get_session),
):
    return LeaveService.create_leave(token, leave_data, session)


@router.get("/leaves/student/{student_id}", response_model=List[Leave])
def read_leaves_by_student(
    token: str, student_id: int, session: Session = Depends(get_session)
):
    return LeaveService.get_leaves_by_student(token, student_id, session)


@router.get("/leaves/reviewer/{reviewer_id}", response_model=List[Leave])
def read_leaves_by_reviewer(
    token: str, reviewer_id: int, session: Session = Depends(get_session)
):
    return LeaveService.get_leaves_by_reviewer(token, reviewer_id, session)


@router.get("/leaves/course/{course_id}", response_model=List[Leave])
def read_leaves_by_course(course_id: int, session: Session = Depends(get_session)):
    return LeaveService.get_leaves_by_course(course_id, session)


@router.get("/leaves/teacher/{teacher_id}", response_model=List[Leave])
def read_leaves_by_teacher(teacher_id: int, session: Session = Depends(get_session)):
    return LeaveService.get_leaves_by_teacher(teacher_id, session)


@router.post("/leaves/edit/{leave_id}", response_model=Leave)
def edit_leave_by_id(
    leave_id: int,
    token: str,
    leave_data: LeaveCreate,
    session: Session = Depends(get_session),
):
    return LeaveService.edit_leave(token, leave_id, leave_data, session)
