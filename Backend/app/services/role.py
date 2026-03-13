from sqlmodel import Session, select, func
from fastapi import Depends, Query, HTTPException

from app.models import Role
from app.services.common import CommonService


class RoleService:
    @staticmethod
    def get_roles(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        session: Session = Depends(lambda: None),
    ):
        """分页获取角色列表"""
        roles, total, total_pages = CommonService.paginate_query(
            session, Role, page, page_size
        )
        return roles, total, total_pages

    @staticmethod
    def get_roles_count(session: Session):
        """获取角色数量"""
        return {
            "roles_count": session.exec(
                select(func.count(Role.role_id))
            ).one()
        }

    @staticmethod
    def get_role_by_id(role_id: int, session: Session):
        """根据ID获取角色"""
        return CommonService.get_by_id(session, Role, role_id, "role_id")

    @staticmethod
    def create_role(role_data: dict, session: Session):
        """创建角色"""
        role = Role(**role_data)
        session.add(role)
        session.commit()
        session.refresh(role)
        return role

    @staticmethod
    def get_or_create_role_by_name(role_name: str, session: Session) -> Role:
        """根据名称获取或创建角色"""
        role = session.exec(
            select(Role).where(Role.role_name == role_name)
        ).first()
        if not role:
            # 创建新角色，使用自增ID
            role = Role(role_name=role_name)
            session.add(role)
            session.commit()
            session.refresh(role)
        return role
