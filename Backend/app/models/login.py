from sqlmodel import SQLModel, Field
from datetime import datetime


class Login(SQLModel, table=True):
    login_id: int = Field(default=None, primary_key=True)
    user_role: str
    user_id: int
    user_name: str
    token: str
    login_time: datetime = Field(default_factory=datetime.now)
    can_be_used: bool = Field(default=True)