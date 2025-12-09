from sqlmodel import SQLModel, Field


class Reviewer(SQLModel, table=True):
    reviewer_id: int = Field(primary_key=True)
    reviewer_name: str = Field(max_length=8)
    school: str = Field(max_length=8, default=None)
    role: str = Field(max_length=10, default=None)
    password: str = Field(max_length=60, default=None)
