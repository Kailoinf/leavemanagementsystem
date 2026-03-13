from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.connection import get_session
from app.models import Course
from app.schemas import PaginatedResponse
from app.services.course import CourseService

router = APIRouter()


@router.get("/courses", response_model=PaginatedResponse)
def read_courses(
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
):
    items, total, total_pages = CourseService.get_courses(page, page_size, session)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/courses/count")
def courses_count(session: Session = Depends(get_session)):
    return CourseService.get_courses_count(session)


@router.get("/courses/{course_id}", response_model=Course)
def read_course(course_id: int, session: Session = Depends(get_session)):
    return CourseService.get_course_by_id(course_id, session)


@router.post("/courses", response_model=Course)
def create_course_endpoint(
    course: Course, session: Session = Depends(get_session)
):
    return CourseService.create_course(course, session)