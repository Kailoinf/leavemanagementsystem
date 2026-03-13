from sqlmodel import Session, select, func
from fastapi import Depends, Query, HTTPException

from app.models import School
from app.services.common import CommonService


class SchoolService:
    @staticmethod
    def get_schools(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        session: Session = Depends(lambda: None),
    ):
        """分页获取学校/院系列表"""
        schools, total, total_pages = CommonService.paginate_query(
            session, School, page, page_size
        )
        return schools, total, total_pages

    @staticmethod
    def get_schools_count(session: Session):
        """获取学校/院系数量"""
        return {
            "schools_count": session.exec(
                select(func.count(School.school_id))
            ).one()
        }

    @staticmethod
    def get_school_by_id(school_id: int, session: Session):
        """根据ID获取学校/院系"""
        return CommonService.get_by_id(session, School, school_id, "school_id")

    @staticmethod
    def create_school(school_data: dict, session: Session):
        """创建学校/院系"""
        school = School(**school_data)
        session.add(school)
        session.commit()
        session.refresh(school)
        return school

    @staticmethod
    def get_or_create_school_by_name(school_name: str, session: Session) -> School:
        """根据名称获取或创建学校/院系"""
        school = session.exec(
            select(School).where(School.school_name == school_name)
        ).first()
        if not school:
            # 创建新学校，使用自增ID
            school = School(school_name=school_name)
            session.add(school)
            session.commit()
            session.refresh(school)
        return school
