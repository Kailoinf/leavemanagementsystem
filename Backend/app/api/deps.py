from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from app.database.connection import get_session
from app.models.login import Login


def check_login(token: str, session: Session = Depends(get_session)):
    """验证登录状态"""
    login_records = session.exec(
        select(Login).where(Login.token == token).order_by(Login.login_id.desc())
    ).all()
    # 找到第一个can_be_used为true的记录
    login_record = next(
        (record for record in login_records if record.can_be_used), None
    )

    if not login_record:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not login_record.can_be_used:
        raise HTTPException(status_code=401, detail="Token is disabled")
    return {
        "role": login_record.user_role,
        "id": login_record.user_id,
        "name": login_record.user_name,
    }


def logout(token: str, session: Session = Depends(get_session)):
    """登出"""
    # 将对应token的登录记录标记为不可用（使用与check_login相同的逻辑）
    login_records = session.exec(
        select(Login).where(Login.token == token).order_by(Login.login_id.desc())
    ).all()
    login_record = next(
        (record for record in login_records if record.can_be_used), None
    )

    if not login_record:
        raise HTTPException(status_code=401, detail="Invalid token")

    login_record.can_be_used = False
    session.add(login_record)
    session.commit()
    return {"message": "Successfully logged out"}