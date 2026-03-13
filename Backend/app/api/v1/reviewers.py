from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database.connection import get_session
from app.models import Reviewer
from app.schemas import ReviewerCreate, PaginatedResponse
from app.services.reviewer import ReviewerService

router = APIRouter()


@router.get("/reviewers", response_model=PaginatedResponse)
def read_reviewers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    reviewers, total, total_pages = ReviewerService.get_reviewers(page, page_size, session)
    return PaginatedResponse(
        items=reviewers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/reviewers/count")
def reviewers_count(session: Session = Depends(get_session)):
    return ReviewerService.get_reviewers_count(session)


@router.get("/reviewers/{reviewer_id}", response_model=Reviewer)
def read_reviewer(reviewer_id: int, session: Session = Depends(get_session)):
    return ReviewerService.get_reviewer_by_id(reviewer_id, session)


@router.post("/reviewers", response_model=Reviewer, summary="创建审核员")
def create_reviewer_endpoint(
    reviewer_data: ReviewerCreate,
    session: Session = Depends(get_session),
):
    return ReviewerService.create_reviewer(reviewer_data, session)