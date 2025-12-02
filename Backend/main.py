from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
import toml
from typing import List
import uvicorn


# 数据模型定义
class Reviewer(SQLModel, table=True):
    staff_id: int = Field(primary_key=True)  # 整数主键默认自增
    name: str = Field(max_length=8)
    department: str = Field(max_length=8, nullable=True)
    role: str = Field(max_length=10, nullable=True)
    password: str = Field(max_length=32, nullable=True)


class User(SQLModel, table=True):
    student_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: str = Field(max_length=32, nullable=True)
    department: str = Field(max_length=8, nullable=True)
    reviewer_id: int = Field(
        max_length=12, foreign_key="reviewer.staff_id", nullable=True
    )
    guarantee_permission: datetime


class Teacher(SQLModel, table=True):
    teacher_id: int = Field(max_length=12, primary_key=True)
    name: str = Field(max_length=8)
    password: str = Field(max_length=32, nullable=True)


class Leave(SQLModel, table=True):
    leave_id: int = Field(max_length=12, primary_key=True)
    student_id: int = Field(foreign_key="user.student_id")
    leave_date: datetime
    class_hours: str = Field(max_length=8, nullable=True)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: str = Field(max_length=8, nullable=True)
    remarks: str = Field(max_length=100, nullable=True)
    materials: str = Field(max_length=100, nullable=True)
    reviewer_id: int = Field(
        max_length=12, foreign_key="reviewer.staff_id", nullable=True
    )
    teacher_id: int = Field(
        max_length=12, foreign_key="teacher.teacher_id", nullable=True
    )
    audit_remarks: str = Field(max_length=100, nullable=True)
    audit_time: datetime = Field(nullable=True)
    course_id: int = Field(max_length=12, foreign_key="course.course_id", nullable=True)
    is_modified: str = Field(max_length=12, nullable=True)
    guarantee_student_id: int = Field(
        max_length=12, foreign_key="user.student_id", nullable=True
    )


class Course(SQLModel, table=True):
    course_id: int = Field(max_length=12, primary_key=True)
    teacher_id: int = Field(max_length=12, foreign_key="teacher.teacher_id")
    course_name: str = Field(max_length=12)
    class_hours: str = Field(max_length=8, nullable=True)


def create_database():
    # 通过config.toml中的信息连接数据库
    try:
        with open("config.toml", "r") as f:
            config = toml.load(f)
            sqlite_url = f"sqlite:///{config['database']['path']}"
            return sqlite_url
    except FileNotFoundError:
        print("Error: config.toml not found")
        exit(1)
    except toml.TomlDecodeError:
        print("Error: config.toml is not a valid TOML file")
        exit(1)


# 创建数据库引擎
sqlite_url = create_database()
engine = create_engine(sqlite_url)
SQLModel.metadata.create_all(engine, checkfirst=True)
app = FastAPI()


# 查询所有用户的函数
def get_all_users(session: Session) -> List[User]:
    statement = select(User)
    return session.exec(statement).all()


# API 端点：获取所有用户
@app.get("/users/", response_model=List[User])
def read_users():
    with Session(engine) as session:
        users = get_all_users(session)
        return users


# 根据 student_id 查询用户的函数
def get_user_by_id(session: Session, student_id: int) -> User:
    statement = select(User).where(User.student_id == student_id)
    return session.exec(statement).first()


# API 端点：根据 student_id 获取用户
@app.get("/users/{student_id}", response_model=User)
def read_user(student_id: int):
    with Session(engine) as session:
        user = get_user_by_id(session, student_id)
        return user


def create_user(session: Session, user: User) -> User:
    # Convert ISO string to datetime object if needed
    if isinstance(user.guarantee_permission, str):
        from datetime import datetime

        user.guarantee_permission = datetime.fromisoformat(user.guarantee_permission)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.post("/users/", response_model=User)
def create_user_endpoint(user: User):
    with Session(engine) as session:
        db_user = create_user(session, user=user)
        return db_user


# 查询所有请假记录的函数
def get_all_leaves(session: Session) -> List[Leave]:
    statement = select(Leave)
    return session.exec(statement).all()


# API 端点：获取所有请假记录
@app.get("/leaves/", response_model=List[Leave])
def read_leaves():
    with Session(engine) as session:
        leaves = get_all_leaves(session)
        return leaves


def create_leave(session: Session, leave: Leave) -> Leave:
    session.add(leave)
    session.commit()
    session.refresh(leave)
    return leave


@app.post("/leaves/", response_model=Leave)
def create_leave_endpoint(leave: Leave):
    with Session(engine) as session:
        db_leave = create_leave(session, leave=leave)
        return db_leave


# 根据 student_id 查询请假记录的函数
def get_leaves_by_student(session: Session, student_id: int) -> List[Leave]:
    statement = select(Leave).where(Leave.student_id == student_id)
    return session.exec(statement).all()


# API 端点：根据 student_id 获取请假记录
@app.get("/leaves/{student_id}", response_model=List[Leave])
def read_leaves_by_student(student_id: int):
    with Session(engine) as session:
        leaves = get_leaves_by_student(session, student_id)
        return leaves


# 根据 reviewer_id 查询请假记录的函数
def get_leaves_by_reviewer(session: Session, reviewer_id: int) -> List[Leave]:
    statement = select(Leave).where(Leave.reviewer_id == reviewer_id)
    return session.exec(statement).all()


# API 端点：根据 reviewer_id 获取请假记录
@app.get("/leaves/reviewer/{reviewer_id}", response_model=List[Leave])
def read_leaves_by_reviewer(reviewer_id: int):
    with Session(engine) as session:
        leaves = get_leaves_by_reviewer(session, reviewer_id)
        return leaves


@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
