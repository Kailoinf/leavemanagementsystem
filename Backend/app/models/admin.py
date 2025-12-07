from sqlmodel import SQLModel, Field


class Admin(SQLModel, table=True):
    admin_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: str = Field(max_length=60, default=None)