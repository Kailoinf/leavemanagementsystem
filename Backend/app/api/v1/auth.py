from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database.connection import get_session
from app.schemas import UserLogin, AdminCreate, ChangePassword
from app.models import Admin, Login
from app.services.auth import AuthService
from app.api.deps import check_login, logout

router = APIRouter()


@router.post("/login", summary="登录")
def login(user: UserLogin, session: Session = Depends(get_session)):
    return AuthService.login(user, session)


@router.get("/login/check")
def login_check(token: str, session: Session = Depends(get_session)):
    """检查登录状态"""
    return check_login(token, session)


@router.get("/logout")
def log_out(token: str, session: Session = Depends(get_session)):
    return logout(token, session)


@router.get("/login/orcode")
def login_qrcode(
    token: str,
    login_token: str,
    session_check: Session = Depends(get_session),
    session_login: Session = Depends(get_session),
):
    obj = check_login(token, session_check)
    if "detail" not in obj:
        login_record = Login(
            user_role=obj["role"],
            user_id=obj["id"],
            user_name=obj["name"],
            token=login_token,
        )
        session_login.add(login_record)
        session_login.commit()
        return {
            "role": obj["role"],
            "id": obj["id"],
            "name": obj["name"],
            "token": login_token,
        }


@router.post("/create/admin")
def create_admin(
    admin_data: AdminCreate,
    session: Session = Depends(get_session),
):
    # 当管理员数为0时可用
    if AuthService.get_admins_count(session) == 0:
        from app.utils.password import hash_password

        admin_data.password = hash_password(admin_data.password)
        admin = Admin(**admin_data.model_dump())
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin
    else:
        raise HTTPException(status_code=400, detail="Admin already exists")


@router.post("/change-password", summary="修改密码")
def change_password(
    token: str,
    password_data: ChangePassword,
    session: Session = Depends(get_session),
):
    """修改密码接口 - 修改自己的密码"""
    return AuthService.change_password(token, password_data, session, None)


@router.post("/change-password/{user_id}", summary="修改指定用户密码")
def change_user_password(
    user_id: int,
    token: str,
    password_data: ChangePassword,
    session: Session = Depends(get_session),
):
    """修改指定用户密码接口 - 仅管理员可用"""
    return AuthService.change_password(token, password_data, session, user_id)
