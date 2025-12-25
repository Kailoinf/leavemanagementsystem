from sqlmodel import SQLModel, Field


class School(SQLModel, table=True):
    """院系表 - 存储二级学院信息"""
    school_id: int = Field(primary_key=True)
    school_name: str = Field(max_length=20, unique=True)  # 院系名称（如：计算机系、软件工程学院等）
