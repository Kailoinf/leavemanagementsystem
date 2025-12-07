from sqlmodel import Session, select, func
from fastapi import HTTPException

from app.schemas import UserLogin
from app.models import Admin, Teacher, Student, Reviewer, Login
from app.utils.password import verify_password


class AuthService:
    @staticmethod
    def login(user: UserLogin, session: Session):
        """用户登录"""
        role_model_map = {
            "teacher": (Teacher, "teacher_id"),
            "student": (Student, "student_id"),
            "reviewer": (Reviewer, "reviewer_id"),
            "admin": (Admin, "admin_id"),
        }
        if user.role not in role_model_map:
            raise HTTPException(400, "Invalid role")

        model_cls, id_field = role_model_map[user.role]
        obj = AuthService.get_by_id(session, model_cls, user.id, id_field)

        if not obj.password:
            raise HTTPException(401, "User has no password set")

        if not verify_password(user.password, obj.password):
            raise HTTPException(401, "Invalid credentials")

        login_record = Login(
            user_role=user.role,
            user_id=user.id,
            user_name=obj.name,
            token=user.token,
        )
        session.add(login_record)
        session.commit()

        return {
            "role": user.role,
            "id": user.id,
            "name": obj.name,
            "token": user.token,  # 返回 token，前端需保存
        }

    @staticmethod
    def get_by_id(session: Session, model, id_value: int, id_field: str):
        """根据ID获取对象"""
        field = getattr(model, id_field)
        stmt = select(model).where(field == id_value)
        obj = session.exec(stmt).first()
        if not obj:
            raise HTTPException(
                404, f"{model.__name__} with {id_field}={id_value} not found"
            )
        return obj

    @staticmethod
    def get_admins_count(session: Session) -> int:
        """获取管理员数量"""
        return session.exec(select(func.count(Admin.admin_id))).one()