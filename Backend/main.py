from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, create_engine, Session, select, func
from datetime import datetime
import toml
from typing import List
from pydantic import BaseModel


# 分页响应模型
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int

class UserLogin(BaseModel):
    role: str
    id: int
    password: str

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


def login_user(user: UserLogin):
    with Session(engine) as session:
        if user.role == "teacher":
            teacher = get_teacher_by_id(session, user.id)
            if teacher and teacher.password == user.password:
                return teacher
        elif user.role == "student":
            student = get_student_by_id(session, user.id)
            if student and student.password == user.password:
                return student
        elif user.role == "reviewer":
            reviewer = get_reviewer_by_id(session, user.id)
            if reviewer and reviewer.password == user.password:
                return reviewer
        else:
            return None

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

def get_teachers_paginated(session: Session, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    statement = select(Teacher).offset(offset).limit(page_size)
    teachers = session.exec(statement).all()

    # 使用高效的计数方法
    total_count = get_teachers_count(session)

    total_pages = (total_count + page_size - 1) // page_size

    return teachers, total_count, total_pages

def get_all_teachers(session: Session) -> List[Teacher]:
    statement = select(Teacher)
    return session.exec(statement).all()

# 根据 teacher_id 查询用户的函数
def get_teacher_by_id(session: Session, teacher_id: int) -> Teacher:
    statement = select(Teacher).where(Teacher.teacher_id == teacher_id)
    return session.exec(statement).first()


def create_teacher(session: Session, teacher: Teacher) -> Teacher:
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


def get_courses_paginated(session: Session, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    statement = select(Course).offset(offset).limit(page_size)
    courses = session.exec(statement).all()

    # 使用高效的计数方法
    total_count = get_courses_count(session)

    total_pages = (total_count + page_size - 1) // page_size

    return courses, total_count, total_pages

def get_all_courses(session: Session) -> List[Course]:
    statement = select(Course)
    return session.exec(statement).all()

def get_course_by_id(session: Session, course_id: int) -> Course:
    statement = select(Course).where(Course.course_id == course_id)
    return session.exec(statement).first()

def create_course(session: Session, course: Course) -> Course:
    session.add(course)
    session.commit()
    session.refresh(course)
    return course

# 分页查询学生的函数
def get_students_paginated(session: Session, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    statement = select(Student).offset(offset).limit(page_size)
    students = session.exec(statement).all()

    # 使用高效的计数方法
    total_count = get_students_count(session)

    total_pages = (total_count + page_size - 1) // page_size

    return students, total_count, total_pages


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


# 分页查询请假记录的函数
def get_leaves_paginated(session: Session, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    statement = select(Leave).offset(offset).limit(page_size)
    leaves = session.exec(statement).all()

    # 使用高效的计数方法
    total_count = get_leaves_count(session)

    total_pages = (total_count + page_size - 1) // page_size

    return leaves, total_count, total_pages


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


# 根据 course_id 查询请假记录的函数
def get_leaves_by_course(session: Session, course_id: int) -> List[Leave]:
    statement = select(Leave).where(Leave.course_id == course_id)
    return session.exec(statement).all()


# 根据 teacher_id 查询请假记录的函数（通过课程关联）
def get_leaves_by_teacher(session: Session, teacher_id: int) -> List[Leave]:
    # 首先获取该教师教授的所有课程
    courses_statement = select(Course.course_id).where(Course.teacher_id == teacher_id)
    course_ids = session.exec(courses_statement).all()

    # 然后获取这些课程的所有请假记录
    if course_ids:
        leaves_statement = select(Leave).where(Leave.course_id.in_(course_ids))
        return session.exec(leaves_statement).all()
    return []


def get_students_count(session: Session):
    """高效获取学生总数，使用SQL COUNT而不是获取所有记录"""
    count_statement = select(func.count(Student.student_id))
    return session.exec(count_statement).one()


def get_reviewers_count(session: Session):
    """高效获取审核员总数，使用SQL COUNT而不是获取所有记录"""
    count_statement = select(func.count(Reviewer.reviewer_id))
    return session.exec(count_statement).one()


def get_leaves_count(session: Session):
    """高效获取请假记录总数，使用SQL COUNT而不是获取所有记录"""
    count_statement = select(func.count(Leave.leave_id))
    return session.exec(count_statement).one()


def get_teachers_count(session: Session):
    """高效获取教师总数，使用SQL COUNT而不是获取所有记录"""
    count_statement = select(func.count(Teacher.teacher_id))
    return session.exec(count_statement).one()


def get_courses_count(session: Session):
    """高效获取课程总数，使用SQL COUNT而不是获取所有记录"""
    count_statement = select(func.count(Course.course_id))
    return session.exec(count_statement).one()


def get_reviewers_paginated(session: Session, page: int = 1, page_size: int = 20):
    offset = (page - 1) * page_size
    statement = select(Reviewer).offset(offset).limit(page_size)
    reviewers = session.exec(statement).all()

    # 使用高效的计数方法
    total_count = get_reviewers_count(session)

    total_pages = (total_count + page_size - 1) // page_size

    return reviewers, total_count, total_pages


def create_reviewer(session: Session, reviewer: Reviewer) -> Reviewer:
    session.add(reviewer)
    session.commit()
    session.refresh(reviewer)
    return reviewer


def get_reviewer_by_id(session: Session, reviewer_id: int) -> Reviewer:
    statement = select(Reviewer).where(Reviewer.reviewer_id == reviewer_id)
    return session.exec(statement).first()


# API 端点：获取所有用户（支持分页）
@app.get("/students", response_model=PaginatedResponse)
def read_students(page: int = 1, page_size: int = 20):
    with Session(engine) as session:
        students, total, total_pages = get_students_paginated(session, page, page_size)

        # 为每个学生添加审核员姓名
        students_with_names = []
        for student in students:
            student_dict = student.model_dump()
            if student.reviewer_id:
                reviewer = get_reviewer_by_id(session, student.reviewer_id)
                student_dict["reviewer_name"] = reviewer.name if reviewer else None
            else:
                student_dict["reviewer_name"] = None
            students_with_names.append(student_dict)

        return PaginatedResponse(
            items=students_with_names,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# API 端点：获取学生的数量
@app.get("/students/count")
def students_count():
    with Session(engine) as session:
        total_count = get_students_count(session)
        return {"students_count": total_count}


# API 端点：根据 student_id 获取学生
@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int):
    with Session(engine) as session:
        student = get_student_by_id(session, student_id)
        return student


# API 端点：创建学生
@app.post("/students", response_model=Student)
def create_student_endpoint(student: Student):
    with Session(engine) as session:
        db_student = create_student(session, student=student)
        return db_student


# API 端点：获取所有请假记录（支持分页）
@app.get("/leaves", response_model=PaginatedResponse)
def read_leaves(page: int = 1, page_size: int = 20):
    with Session(engine) as session:
        leaves, total, total_pages = get_leaves_paginated(session, page, page_size)

        # 为每个请假记录添加关联数据的名称
        leaves_with_names = []
        for leave in leaves:
            leave_dict = leave.model_dump()

            # 添加学生姓名
            if leave.student_id:
                student = get_student_by_id(session, leave.student_id)
                leave_dict["student_name"] = student.name if student else None

            # 添加审核员姓名
            if leave.reviewer_id:
                reviewer = get_reviewer_by_id(session, leave.reviewer_id)
                leave_dict["reviewer_name"] = reviewer.name if reviewer else None

            # 添加教师姓名
            if leave.teacher_id:
                teacher = get_teacher_by_id(session, leave.teacher_id)
                leave_dict["teacher_name"] = teacher.name if teacher else None

            # 添加课程名称
            if leave.course_id:
                course = get_course_by_id(session, leave.course_id)
                leave_dict["course_name"] = course.course_name if course else None

            # 添加担保学生姓名
            if leave.guarantee_student_id:
                guarantee_student = get_student_by_id(session, leave.guarantee_student_id)
                leave_dict["guarantee_student_name"] = guarantee_student.name if guarantee_student else None

            leaves_with_names.append(leave_dict)

        return PaginatedResponse(
            items=leaves_with_names,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# API 端点：获取请假记录数
@app.get("/leaves/count")
def leaves_count():
    with Session(engine) as session:
        total_count = get_leaves_count(session)
        return {"leaves_count": total_count}


# API 端点：创建请假记录
@app.post("/leaves", response_model=Leave)
def create_leave_endpoint(leave: Leave):
    with Session(engine) as session:
        db_leave = create_leave(session, leave=leave)
        return db_leave


# API 端点：根据 student_id 获取请假记录
@app.get("/leaves/student/{student_id}", response_model=List[Leave])
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


# API 端点：根据 course_id 获取请假记录
@app.get("/leaves/course/{course_id}", response_model=List[Leave])
def read_leaves_by_course(course_id: int):
    with Session(engine) as session:
        leaves = get_leaves_by_course(session, course_id)
        return leaves


# API 端点：根据 teacher_id 获取请假记录
@app.get("/leaves/teacher/{teacher_id}", response_model=List[Leave])
def read_leaves_by_teacher(teacher_id: int):
    with Session(engine) as session:
        leaves = get_leaves_by_teacher(session, teacher_id)
        return leaves

# API 端点：获取教师的数量
@app.get("/teachers/count")
def teachers_count():
    with Session(engine) as session:
        total_count = get_teachers_count(session)
        return {"teachers_count": total_count}


# API 端点：根据 teacher_id 获取教师
@app.get("/teachers/{teacher_id}", response_model=Teacher)
def read_teacher(teacher_id: int):
    with Session(engine) as session:
        teacher = get_teacher_by_id(session, teacher_id)
        return teacher


# API 端点：分页查询教师
@app.get("/teachers", response_model=PaginatedResponse)
def read_teachers(page: int = 1, page_size: int = 20):
    with Session(engine) as session:
        teachers, total, total_pages = get_teachers_paginated(
            session, page, page_size
        )
        return PaginatedResponse(
            items=teachers,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# API 端点：创建教师
@app.post("/teachers", response_model=Teacher)
def create_teacher_endpoint(teacher: Teacher):
    with Session(engine) as session:
        teacher = create_teacher(session, teacher)
        return teacher


# API 端点：获取课程的数量
@app.get("/courses/count")
def courses_count():
    with Session(engine) as session:
        total_count = get_courses_count(session)
        return {"courses_count": total_count}


# API 端点：根据 course_id 获取课程
@app.get("/courses/{course_id}", response_model=Course)
def read_course(course_id: int):
    with Session(engine) as session:
        course = get_course_by_id(session, course_id)
        return course


# API 端点：分页查询课程
@app.get("/courses", response_model=PaginatedResponse)
def read_courses(page: int = 1, page_size: int = 20):
    with Session(engine) as session:
        courses, total, total_pages = get_courses_paginated(
            session, page, page_size
        )

        # 为每个课程添加教师姓名
        courses_with_teacher = []
        for course in courses:
            course_dict = course.model_dump()
            if course.teacher_id:
                teacher = get_teacher_by_id(session, course.teacher_id)
                course_dict["teacher_name"] = teacher.name if teacher else None
            else:
                course_dict["teacher_name"] = None
            courses_with_teacher.append(course_dict)

        return PaginatedResponse(
            items=courses_with_teacher,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# API 端点：创建课程
@app.post("/courses", response_model=Course)
def create_course_endpoint(course: Course):
    with Session(engine) as session:
        course = create_course(session, course)
        return course


@app.get("/reviewers", response_model=PaginatedResponse)
def read_reviewers(page: int = 1, page_size: int = 20):
    with Session(engine) as session:
        reviewers, total, total_pages = get_reviewers_paginated(
            session, page, page_size
        )
        return PaginatedResponse(
            items=reviewers,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


# 将此端点移到 read_reviewer 之前以避免路径冲突
@app.get("/reviewers/count")
def reviewers_count():
    with Session(engine) as session:
        total_count = get_reviewers_count(session)
        return {"reviewers_count": total_count}


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

@app.post("/login")
def login(user:UserLogin):
    return login_user(user)


@app.get("/")
async def read_root():
    return {"Status": "Working"}
