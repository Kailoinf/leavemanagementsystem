from pydantic import BaseModel


class UserLogin(BaseModel):
    id: int
    password: str


class ChangePassword(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str
