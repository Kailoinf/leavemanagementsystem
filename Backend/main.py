import logging
from datetime import datetime, timedelta
from typing import List, Optional, Type, Any, Dict

import bcrypt
import toml
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session, select, func

# =======================
# 🔐 配置与日志
# =======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_database_url() -> str:
    try:
        config = toml.load("config.toml")
        db_path = config["database"]["path"]
        return f"sqlite:///{db_path}"
    except FileNotFoundError:
        logger.error("❌ config.toml not found")
        raise RuntimeError("Database config missing")
    except toml.TomlDecodeError as e:
        logger.error(f"❌ Invalid TOML: {e}")
        raise RuntimeError("Database config corrupted")


# =======================
# 🔑 密码工具
# =======================
def hash_password(plain: str) -> str:
    """明文 -> bcrypt 密文"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文 vs bcrypt 密文"""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# =======================
# 📦 数据模型（已移除明文兼容逻辑，仅保留哈希标记）
# =======================
class Reviewer(SQLModel, table=True):
    reviewer_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    school: Optional[str] = Field(max_length=8, default=None)
    role: Optional[str] = Field(max_length=10, default=None)
    password: Optional[str] = Field(
        max_length=60, default=None
    )  # bcrypt hash ~60 chars
    password_is_hashed: bool = Field(
        default=True
    )  # 默认为 True，表示新创建的用户密码已加密


class Student(SQLModel, table=True):
    student_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: Optional[str] = Field(max_length=60, default=None)
    password_is_hashed: bool = Field(default=True)  # 默认为 True
    school: Optional[str] = Field(max_length=8, default=None)
    reviewer_id: Optional[int] = Field(foreign_key="reviewer.reviewer_id", default=None)
    guarantee_permission: datetime = Field(default=datetime.now() - timedelta(days=1))


class Teacher(SQLModel, table=True):
    teacher_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: Optional[str] = Field(max_length=60, default=None)
    password_is_hashed: bool = Field(default=True)  # 默认为 True


class Course(SQLModel, table=True):
    course_id: int = Field(primary_key=True)
    teacher_id: int = Field(foreign_key="teacher.teacher_id")
    course_name: str = Field(max_length=12)
    class_hours: Optional[str] = Field(max_length=8, default=None)


class Leave(SQLModel, table=True):
    leave_id: int = Field(primary_key=True)
    student_id: int = Field(foreign_key="student.student_id")
    leave_date: datetime
    class_hours: Optional[str] = Field(max_length=8, default=None)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: Optional[str] = Field(max_length=8, default=None)
    remarks: Optional[str] = Field(max_length=100, default=None)
    materials: Optional[str] = Field(max_length=100, default=None)
    reviewer_id: Optional[int] = Field(foreign_key="reviewer.reviewer_id", default=None)
    teacher_id: Optional[int] = Field(foreign_key="teacher.teacher_id", default=None)
    audit_remarks: Optional[str] = Field(max_length=100, default=None)
    audit_time: Optional[datetime] = None
    course_id: Optional[int] = Field(foreign_key="course.course_id", default=None)
    is_modified: Optional[str] = Field(max_length=12, default=None)
    guarantee_student_id: Optional[int] = Field(
        foreign_key="student.student_id", default=None
    )


class Login(SQLModel, table=True):
    login_id: int = Field(primary_key=True, default=None)
    user_role: str
    user_id: int
    token: str
    login_time: datetime = Field(default=datetime.now())
    can_be_used: bool = Field(default=True)


# =======================
# 🧩 Pydantic 响应模型
# =======================
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserLogin(BaseModel):
    role: str
    id: int
    password: str
    token: str


# =======================
# 🗄️ 数据库管理器
# =======================
class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(load_database_url(), echo=False)
        SQLModel.metadata.create_all(self.engine, checkfirst=True)

    def get_session(self):
        with Session(self.engine) as session:
            yield session


db_manager = DatabaseManager()
app = FastAPI(title="Leave Management System", version="2.0")


# =======================
# 🔌 中间件
# =======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =======================
# 🛠️ 通用工具函数
# =======================
def paginate_query(
    session: Session, model: Type[SQLModel], page: int = 1, page_size: int = 20
) -> tuple[List[SQLModel], int, int]:
    """通用分页查询（动态主键支持）"""
    if page < 1 or page_size < 1:
        raise HTTPException(
            status_code=400, detail="Page and page_size must be positive"
        )

    offset = (page - 1) * page_size
    items = session.exec(select(model).offset(offset).limit(page_size)).all()

    # 🔑 动态获取主键列（兼容 student_id / leave_id 等）
    pk_cols = model.__table__.primary_key.columns
    if not pk_cols:
        raise RuntimeError(f"Model {model.__name__} has no primary key")
    pk_col = list(pk_cols)[0]
    total = session.exec(select(func.count(pk_col))).one()

    total_pages = (total + page_size - 1) // page_size
    return items, total, total_pages


def get_by_id(session: Session, model: Type[SQLModel], id_value: int, id_field: str):
    field = getattr(model, id_field)
    stmt = select(model).where(field == id_value)
    obj = session.exec(stmt).first()
    if not obj:
        raise HTTPException(
            404, f"{model.__name__} with {id_field}={id_value} not found"
        )
    return obj


def inject_relations(
    session: Session, items: List[SQLModel], relation_fields: Dict[str, tuple]
) -> List[dict]:
    """批量注入关联数据（避免 N+1）"""
    item_dicts = [item.model_dump() for item in items]

    # 收集 ID
    id_map: Dict[type, set] = {}
    for field, (rel_model, _) in relation_fields.items():
        ids = {d[field] for d in item_dicts if d.get(field)}
        if ids:
            id_map[rel_model] = id_map.get(rel_model, set()) | ids

    # 批量查
    cache: Dict[type, Dict[int, Any]] = {}
    for rel_model, ids in id_map.items():
        pk_name = rel_model.__table__.primary_key.columns.keys()[0]
        pk_attr = getattr(rel_model, pk_name)
        stmt = select(rel_model).where(pk_attr.in_(ids))
        objs = session.exec(stmt).all()
        cache[rel_model] = {getattr(obj, pk_name): obj for obj in objs}

    # 注入
    for d in item_dicts:
        for field, (rel_model, alias) in relation_fields.items():
            rid = d.get(field)
            if rid and rel_model in cache and rid in cache[rel_model]:
                obj = cache[rel_model][rid]
                d[alias] = getattr(obj, "name", None)
            else:
                d[alias] = None

    return item_dicts


# =======================
# 🌐 依赖项
# =======================
def get_db_session():
    return next(db_manager.get_session())


def check_login(token: str, session: Session = Depends(get_db_session)):
    # 查找登录记录
    login_record = session.exec(select(Login).where(Login.token == token)).first()

    # 如果没有找到记录，抛出异常
    if not login_record:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 如果记录不可用，抛出异常
    if not login_record.can_be_used:
        raise HTTPException(status_code=401, detail="Token is disabled")

    # 返回角色和ID
    return {"role": login_record.user_role, "id": login_record.user_id}


# =======================
# 📡 API 路由
# =======================


@app.get("/", summary="健康检查")
async def root():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# --- 学生 ---
@app.get("/students", response_model=PaginatedResponse, summary="分页获取学生列表")
def read_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    students, total, total_pages = paginate_query(session, Student, page, page_size)
    items = inject_relations(
        session, students, {"reviewer_id": (Reviewer, "reviewer_name")}
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/students/count")
def students_count(session: Session = Depends(get_db_session)):
    return {
        "students_count": session.exec(select(func.count(Student.student_id))).one()
    }


@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int, session: Session = Depends(get_db_session)):
    return get_by_id(session, Student, student_id, "student_id")


@app.post("/students", response_model=Student, summary="创建学生")
def create_student_endpoint(
    student: Student, session: Session = Depends(get_db_session)
):
    if student.password:
        student.password = hash_password(student.password)

    if isinstance(student.guarantee_permission, str):
        try:
            student.guarantee_permission = datetime.fromisoformat(
                student.guarantee_permission
            )
        except ValueError:
            raise HTTPException(400, "Invalid datetime format for guarantee_permission")
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


# --- 教师 ---
@app.get("/teachers", response_model=PaginatedResponse)
def read_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    teachers, total, total_pages = paginate_query(session, Teacher, page, page_size)
    return PaginatedResponse(
        items=teachers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/teachers/count")
def teachers_count(session: Session = Depends(get_db_session)):
    return {
        "teachers_count": session.exec(select(func.count(Teacher.teacher_id))).one()
    }


@app.get("/teachers/{teacher_id}", response_model=Teacher)
def read_teacher(teacher_id: int, session: Session = Depends(get_db_session)):
    return get_by_id(session, Teacher, teacher_id, "teacher_id")


@app.post("/teachers", response_model=Teacher, summary="创建教师")
def create_teacher_endpoint(
    teacher: Teacher, session: Session = Depends(get_db_session)
):
    if teacher.password:
        teacher.password = hash_password(teacher.password)
        # password_is_hashed 默认为 True
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


# --- 课程 ---
@app.get("/courses", response_model=PaginatedResponse)
def read_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    courses, total, total_pages = paginate_query(session, Course, page, page_size)
    items = inject_relations(
        session, courses, {"teacher_id": (Teacher, "teacher_name")}
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/courses/count")
def courses_count(session: Session = Depends(get_db_session)):
    return {"courses_count": session.exec(select(func.count(Course.course_id))).one()}


@app.get("/courses/{course_id}", response_model=Course)
def read_course(course_id: int, session: Session = Depends(get_db_session)):
    return get_by_id(session, Course, course_id, "course_id")


@app.post("/courses", response_model=Course)
def create_course_endpoint(course: Course, session: Session = Depends(get_db_session)):
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


# --- 审核员 ---
@app.get("/reviewers", response_model=PaginatedResponse)
def read_reviewers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    reviewers, total, total_pages = paginate_query(session, Reviewer, page, page_size)
    return PaginatedResponse(
        items=reviewers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/reviewers/count")
def reviewers_count(session: Session = Depends(get_db_session)):
    return {
        "reviewers_count": session.exec(select(func.count(Reviewer.reviewer_id))).one()
    }


@app.get("/reviewers/{reviewer_id}", response_model=Reviewer)
def read_reviewer(reviewer_id: int, session: Session = Depends(get_db_session)):
    return get_by_id(session, Reviewer, reviewer_id, "reviewer_id")


@app.post("/reviewers", response_model=Reviewer, summary="创建审核员")
def create_reviewer_endpoint(
    reviewer: Reviewer, session: Session = Depends(get_db_session)
):
    if reviewer.password:
        reviewer.password = hash_password(reviewer.password)
        # password_is_hashed 默认为 True
    session.add(reviewer)
    session.commit()
    session.refresh(reviewer)
    return reviewer


# --- 请假记录 ---
@app.get("/leaves", response_model=PaginatedResponse)
def read_leaves(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_db_session),
):
    leaves, total, total_pages = paginate_query(session, Leave, page, page_size)
    items = inject_relations(
        session,
        leaves,
        {
            "student_id": (Student, "student_name"),
            "reviewer_id": (Reviewer, "reviewer_name"),
            "teacher_id": (Teacher, "teacher_name"),
            "guarantee_student_id": (Student, "guarantee_student_name"),
        },
    )
    # 手动补 course_name（因 Course 无 name 字段）
    for item in items:
        if item.get("course_id"):
            course = session.get(Course, item["course_id"])
            item["course_name"] = course.course_name if course else None
        else:
            item["course_name"] = None
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/leaves/count")
def leaves_count(session: Session = Depends(get_db_session)):
    return {"leaves_count": session.exec(select(func.count(Leave.leave_id))).one()}


@app.post("/leaves", response_model=Leave)
def create_leave_endpoint(leave: Leave, session: Session = Depends(get_db_session)):
    session.add(leave)
    session.commit()
    session.refresh(leave)
    return leave


@app.get("/leaves/student/{student_id}", response_model=List[Leave])
def read_leaves_by_student(student_id: int, session: Session = Depends(get_db_session)):
    return session.exec(select(Leave).where(Leave.student_id == student_id)).all()


@app.get("/leaves/reviewer/{reviewer_id}", response_model=List[Leave])
def read_leaves_by_reviewer(
    reviewer_id: int, session: Session = Depends(get_db_session)
):
    return session.exec(select(Leave).where(Leave.reviewer_id == reviewer_id)).all()


@app.get("/leaves/course/{course_id}", response_model=List[Leave])
def read_leaves_by_course(course_id: int, session: Session = Depends(get_db_session)):
    return session.exec(select(Leave).where(Leave.course_id == course_id)).all()


@app.get("/leaves/teacher/{teacher_id}", response_model=List[Leave])
def read_leaves_by_teacher(teacher_id: int, session: Session = Depends(get_db_session)):
    course_ids = session.exec(
        select(Course.course_id).where(Course.teacher_id == teacher_id)
    ).all()
    if not course_ids:
        return []
    return session.exec(select(Leave).where(Leave.course_id.in_(course_ids))).all()


# --- 🔐 登录  ---
@app.post("/login", summary="登录")
def login(user: UserLogin, session: Session = Depends(get_db_session)):
    role_model_map = {
        "teacher": (Teacher, "teacher_id"),
        "student": (Student, "student_id"),
        "reviewer": (Reviewer, "reviewer_id"),
    }

    if user.role not in role_model_map:
        raise HTTPException(400, "Invalid role")

    model_cls, id_field = role_model_map[user.role]
    obj = get_by_id(session, model_cls, user.id, id_field)

    if not obj.password:
        raise HTTPException(401, "User has no password set")

    # 假设所有现有密码都已加密，直接进行 bcrypt 验证
    if verify_password(user.password, obj.password):
        authenticated = True
    else:
        authenticated = False

    if not authenticated:
        raise HTTPException(401, "Invalid credentials")

    # 把账号角色id都存到一个表中，作为已登录的账号
    login_record = Login(
        user_role=user.role,
        user_id=user.id,
        token=user.token,
    )
    session.add(login_record)
    session.commit()

    return {
        "role": user.role,
        "id": user.id,
        "name": obj.name,
    }


@app.get("/login/check")
def login_check(token: str, session: Session = Depends(get_db_session)):
    """检查登录状态"""
    return check_login(token, session)
