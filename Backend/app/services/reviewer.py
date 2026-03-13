from sqlmodel import Session, select, func
from fastapi import Depends, Query, HTTPException

from app.models import Reviewer, School, Role
from app.schemas import ReviewerCreate
from app.api.deps import check_login
from app.services.common import CommonService
from app.utils.password import hash_password


class ReviewerService:
    @staticmethod
    def get_reviewers(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        session: Session = Depends(lambda: None),
    ):
        """分页获取审核员列表"""
        reviewers, total, total_pages = CommonService.paginate_query(
            session, Reviewer, page, page_size
        )

        # 注入关联数据
        items = CommonService.inject_relations(
            session,
            reviewers,
            {
                "school_id": (
                    School,
                    "school_id",
                    "school_name",
                    "school_name",
                ),
                "role_id": (
                    Role,
                    "role_id",
                    "role_name",
                    "role_name",
                )
            },
        )

        return items, total, total_pages

    @staticmethod
    def get_reviewers_count(session: Session):
        """获取审核员数量"""
        return {
            "reviewers_count": session.exec(
                select(func.count(Reviewer.reviewer_id))
            ).one()
        }

    @staticmethod
    def get_reviewer_by_id(reviewer_id: int, session: Session):
        """根据ID获取审核员"""
        return CommonService.get_by_id(session, Reviewer, reviewer_id, "reviewer_id")

    @staticmethod
    def create_reviewer(
        token: str,
        reviewer_data: ReviewerCreate,
        session: Session,
    ):
        obj = check_login(token, session)
        if obj["role"] not in ["admin"]:
            raise HTTPException(status_code=403, detail="Permission denied")
        """创建审核员"""
        reviewer = Reviewer(**reviewer_data.model_dump())
        if reviewer.password:
            reviewer.password = hash_password(reviewer.password)
        session.add(reviewer)
        session.commit()
        session.refresh(reviewer)
        return reviewer
