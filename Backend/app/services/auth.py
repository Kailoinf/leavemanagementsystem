from sqlmodel import Session, select, func
from fastapi import HTTPException

from app.schemas import UserLogin, ChangePassword
from app.models import Admin, Teacher, Student, Reviewer, Login
from app.utils.password import verify_password, hash_password


class AuthService:
    @staticmethod
    def get_role_model_map():
        """获取角色与模型的映射关系"""
        return {
            "teacher": (Teacher, "teacher_id"),
            "student": (Student, "student_id"),
            "reviewer": (Reviewer, "reviewer_id"),
            "admin": (Admin, "admin_id"),
        }

    @staticmethod
    def find_user_by_id(user_id: int, session: Session):
        """根据用户ID自动检测并返回用户对象和角色"""
        role_model_map = AuthService.get_role_model_map()

        for role, (model, field) in role_model_map.items():
            try:
                obj = AuthService.get_by_id(session, model, user_id, field)
                return obj, role, model, field
            except HTTPException:
                continue

        raise HTTPException(404, "User not found")

    @staticmethod
    def get_user_name_by_role(obj, role: str):
        """根据角色获取正确的用户名字段"""
        name_field_map = {
            "teacher": "teacher_name",
            "student": "student_name",
            "reviewer": "reviewer_name",
            "admin": "name",
        }
        return getattr(obj, name_field_map.get(role, "name"))

    @staticmethod
    def login(user: UserLogin, session: Session):
        """用户登录"""
        # 自动检测用户角色
        obj, user_role, model_cls, id_field = AuthService.find_user_by_id(user.id, session)

        if not obj.password:
            raise HTTPException(401, "User has no password set")

        if not verify_password(user.password, obj.password):
            raise HTTPException(401, "Invalid credentials")

        # 获取用户名
        user_name = AuthService.get_user_name_by_role(obj, user_role)

        login_record = Login(
            user_role=user_role,
            user_id=user.id,
            user_name=user_name,
            token=user.token,
        )
        session.add(login_record)
        session.commit()

        return {
            "role": user_role,
            "id": user.id,
            "name": user_name,
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

    @staticmethod
    def change_password(token: str, password_data: ChangePassword, session: Session, target_user_id: int = None):
        """修改密码"""
        # 验证登录状态并获取用户信息
        from app.api.deps import check_login
        current_user = check_login(token, session)

        # 验证当前用户角色
        role_model_map = AuthService.get_role_model_map()
        if current_user["role"] not in role_model_map:
            raise HTTPException(400, "Invalid role")

        # 确定要修改密码的用户
        if target_user_id is not None:
            # 修改指定用户的密码 - 仅管理员可用
            if current_user["role"] != "admin":
                raise HTTPException(403, "Only admins can change other users' passwords")

            # 查找目标用户
            target_user, target_role, _, _ = AuthService.find_user_by_id(target_user_id, session)
        else:
            # 修改自己的密码
            target_user_id = current_user["id"]
            target_user, target_role, _, _ = AuthService.find_user_by_id(target_user_id, session)

        # 验证原密码 - 管理员可以跳过验证
        if current_user["role"] != "admin":
            if not target_user.password:
                raise HTTPException(400, "User has no password set")

            if not verify_password(password_data.old_password, target_user.password):
                raise HTTPException(400, "Original password is incorrect")

        # 更新密码
        target_user.password = hash_password(password_data.new_password)
        session.commit()

        return {
            "message": "Password changed successfully",
            "target_user_id": target_user_id,
            "target_role": target_role
        }