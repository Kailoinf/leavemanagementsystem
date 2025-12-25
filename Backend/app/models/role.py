from sqlmodel import SQLModel, Field


class Role(SQLModel, table=True):
    """角色表"""
    role_id: int = Field(primary_key=True)
    role_name: str = Field(max_length=20, unique=True)  # 角色名称：系主任、辅导员等
