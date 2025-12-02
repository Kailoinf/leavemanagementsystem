from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime
import toml
from typing import List


# 数据模型定义
class Reviewer(SQLModel, table=True):
    reviewer_id: int = Field(primary_key=True, default=None)  # 整数主键默认自增
    name: str = Field(max_length=8)
    department: str = Field(max_length=8, nullable=True)
    role: str = Field(max_length=10, nullable=True)
    password: str = Field(max_length=32, nullable=True)


class Student(SQLModel, table=True):
    student_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: str = Field(max_length=32, nullable=True)
    department: str = Field(max_length=8, nullable=True)
    reviewer_id: int = Field(
        max_length=12, foreign_key="reviewer.reviewer_id", nullable=True
    )
    guarantee_permission: datetime


class Teacher(SQLModel, table=True):
    teacher_id: int = Field(max_length=12, primary_key=True)
    name: str = Field(max_length=8)
    password: str = Field(max_length=32, nullable=True)


class Leave(SQLModel, table=True):
    leave_id: int = Field(max_length=12, primary_key=True)
    student_id: int = Field(foreign_key="student.student_id")
    leave_date: datetime
    class_hours: str = Field(max_length=8, nullable=True)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: str = Field(max_length=8, nullable=True)
    remarks: str = Field(max_length=100, nullable=True)
    materials: str = Field(max_length=100, nullable=True)
    reviewer_id: int = Field(
        max_length=12, foreign_key="reviewer.reviewer_id", nullable=True
    )
    teacher_id: int = Field(
        max_length=12, foreign_key="teacher.teacher_id", nullable=True
    )
    audit_remarks: str = Field(max_length=100, nullable=True)
    audit_time: datetime = Field(nullable=True)
    course_id: int = Field(max_length=12, foreign_key="course.course_id", nullable=True)
    is_modified: str = Field(max_length=12, nullable=True)
    guarantee_student_id: int = Field(
        max_length=12, foreign_key="student.student_id", nullable=True
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

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 查询所有用户的函数
def get_all_students(session: Session) -> List[Student]:
    statement = select(Student)
    return session.exec(statement).all()


# 根据 student_id 查询用户的函数
def get_student_by_id(session: Session, student_id: int) -> Student:
    statement = select(Student).where(Student.student_id == student_id)
    return session.exec(statement).first()


def create_student(session: Session, student: Student) -> Student:
    # Convert ISO string to datetime object if needed
    if isinstance(student.guarantee_permission, str):
        from datetime import datetime

        student.guarantee_permission = datetime.fromisoformat(
            student.guarantee_permission
        )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


# 查询所有请假记录的函数
def get_all_leaves(session: Session) -> List[Leave]:
    statement = select(Leave)
    return session.exec(statement).all()


def create_leave(session: Session, leave: Leave) -> Leave:
    session.add(leave)
    session.commit()
    session.refresh(leave)
    return leave


# 根据 student_id 查询请假记录的函数
def get_leaves_by_student(session: Session, student_id: int) -> List[Leave]:
    statement = select(Leave).where(Leave.student_id == student_id)
    return session.exec(statement).all()


# 根据 reviewer_id 查询请假记录的函数
def get_leaves_by_reviewer(session: Session, reviewer_id: int) -> List[Leave]:
    statement = select(Leave).where(Leave.reviewer_id == reviewer_id)
    return session.exec(statement).all()


def get_all_reviewsrs(session: Session) -> List[Reviewer]:
    statement = select(Reviewer)
    return session.exec(statement).all()


def create_reviewer(session: Session, reviewer: Reviewer) -> Reviewer:
    session.add(reviewer)
    session.commit()
    session.refresh(reviewer)
    return reviewer


def get_reviewer_by_id(session: Session, reviewer_id: int) -> Reviewer:
    statement = select(Reviewer).where(Reviewer.reviewer_id == reviewer_id)
    return session.exec(statement).first()


# API 端点：获取所有用户
@app.get("/students/", response_model=List[Student])
def read_students():
    with Session(engine) as session:
        students = get_all_students(session)
        return students


# API 端点：获取学生的数量
@app.get("/students/count")
def students_count():
    with Session(engine) as session:
        students = get_all_students(session)
        return {"students_count": len(students)}


# API 端点：根据 student_id 获取学生
@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int):
    with Session(engine) as session:
        student = get_student_by_id(session, student_id)
        return student


# API 端点：创建学生
@app.post("/students/", response_model=Student)
def create_student_endpoint(student: Student):
    with Session(engine) as session:
        db_student = create_student(session, student=student)
        return db_student


# API 端点：获取所有请假记录
@app.get("/leaves/", response_model=List[Leave])
def read_leaves():
    with Session(engine) as session:
        leaves = get_all_leaves(session)
        return leaves


# API 端点：获取请假记录数
@app.get("/leaves/count")
def leaves_count():
    with Session(engine) as session:
        leaves = get_all_leaves(session)
        return {"leaves_count": len(leaves)}


# API 端点：创建请假记录
@app.post("/leaves/", response_model=Leave)
def create_leave_endpoint(leave: Leave):
    with Session(engine) as session:
        db_leave = create_leave(session, leave=leave)
        return db_leave


# API 端点：根据 student_id 获取请假记录
@app.get("/leaves/{student_id}", response_model=List[Leave])
def read_leaves_by_student(student_id: int):
    with Session(engine) as session:
        leaves = get_leaves_by_student(session, student_id)
        return leaves


# API 端点：根据 reviewer_id 获取请假记录
@app.get("/leaves/reviewer/{reviewer_id}", response_model=List[Leave])
def read_leaves_by_reviewer(reviewer_id: int):
    with Session(engine) as session:
        leaves = get_leaves_by_reviewer(session, reviewer_id)
        return leaves


@app.get("/reviewers")
def read_reviewers():
    with Session(engine) as session:
        reviewers = get_all_reviewsrs(session)
        return reviewers


# 将此端点移到 read_reviewer 之前以避免路径冲突
@app.get("/reviewers/count")
def reviewers_count():
    with Session(engine) as session:
        reviewer = get_all_reviewsrs(session)
        return {"reviewers_count": len(reviewer)}


@app.get("/reviewers/{reviewer_id}")
def read_reviewer(reviewer_id: int):
    with Session(engine) as session:
        reviewer = get_reviewer_by_id(session, reviewer_id)
        return reviewer


@app.post("/reviewers")
def create_reviewer_endpoint(reviewer: Reviewer):
    with Session(engine) as session:
        reviewer = create_reviewer(session, reviewer)
        return reviewer


@app.get("/")
async def read_root():
    return {"Status": "Working"}
