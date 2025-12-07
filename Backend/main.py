import logging
from datetime import datetime
from typing import List, Optional, Type, Any, Dict, Union

import bcrypt
import toml
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
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
# 📦 数据模型
# =======================
class Admin(SQLModel, table=True):
    admin_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: Optional[str] = Field(max_length=60, default=None)


class Reviewer(SQLModel, table=True):
    reviewer_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    school: Optional[str] = Field(max_length=8, default=None)
    role: Optional[str] = Field(max_length=10, default=None)
    password: Optional[str] = Field(max_length=60, default=None)


class Student(SQLModel, table=True):
    student_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: Optional[str] = Field(max_length=60, default=None)
    school: Optional[str] = Field(max_length=8, default=None)
    reviewer_id: Optional[int] = Field(foreign_key="reviewer.reviewer_id", default=None)
    guarantee_permission: datetime


class Teacher(SQLModel, table=True):
    teacher_id: int = Field(primary_key=True)
    name: str = Field(max_length=8)
    password: Optional[str] = Field(max_length=60, default=None)


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
    login_id: Optional[int] = Field(default=None, primary_key=True)
    user_role: str
    user_id: int
    user_name: str
    token: str
    login_time: datetime = Field(default_factory=datetime.now)
    can_be_used: bool = Field(default=True)


# =======================
# 🧩 Pydantic 模型
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


class StudentCreate(BaseModel):
    student_id: int
    name: str = Field(max_length=8)
    password: Optional[str] = None
    school: Optional[str] = Field(max_length=8, default=None)
    reviewer_id: Optional[int] = None
    guarantee_permission: Union[datetime, str]

    @field_validator("guarantee_permission", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class TeacherCreate(BaseModel):
    teacher_id: int
    name: str = Field(max_length=8)
    password: Optional[str] = None


class ReviewerCreate(BaseModel):
    reviewer_id: int
    name: str = Field(max_length=8)
    school: Optional[str] = Field(max_length=8, default=None)
    role: Optional[str] = Field(max_length=10, default=None)
    password: Optional[str] = None


class LeaveCreate(BaseModel):
    student_id: int
    leave_date: Union[datetime, str]
    class_hours: Optional[str] = Field(max_length=8, default=None)
    leave_days: str = Field(max_length=8)
    status: str = Field(max_length=8)
    leave_type: Optional[str] = Field(max_length=8, default=None)
    remarks: Optional[str] = Field(max_length=100, default=None)
    materials: Optional[str] = Field(max_length=100, default=None)
    reviewer_id: Optional[int] = None
    teacher_id: Optional[int] = None
    audit_remarks: Optional[str] = Field(max_length=100, default=None)
    audit_time: Optional[Union[datetime, str]] = None
    course_id: Optional[int] = None
    is_modified: Optional[str] = Field(max_length=12, default=None)
    guarantee_student_id: Optional[int] = None

    @field_validator("leave_date", "audit_time", mode="before")
    @classmethod
    def parse_optional_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v


class AdminCreate(BaseModel):
    admin_id: int
    name: str = Field(max_length=8)
    password: Optional[str] = None


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
app = FastAPI(title="Leave Management System")


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

    # 🔑 动态获取主键列
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
    session: Session,
    items: List[SQLModel],
    relation_map: Dict[
        str, tuple
    ],  # field -> (model, pk_attr_name, target_attr, alias)
) -> List[dict]:
    item_dicts = [item.model_dump() for item in items]

    # 收集各模型需查询的 ID
    id_map: Dict[type, set] = {}
    for field, (rel_model, pk_attr_name, _, _) in relation_map.items():
        ids = {d[field] for d in item_dicts if d.get(field) is not None}
        if ids:
            id_map[rel_model] = id_map.get(rel_model, set()) | ids

    # 批量查询并缓存
    cache: Dict[type, Dict[Any, Any]] = {}
    for rel_model, ids in id_map.items():
        # 找到这个模型对应的第一个relation配置
        relation_key = [k for k in relation_map if relation_map[k][0] == rel_model][0]
        pk_attr_name = relation_map[relation_key][1]  # 获取主键属性名

        pk_attr = getattr(rel_model, pk_attr_name)  # 获取主键属性
        stmt = select(rel_model).where(pk_attr.in_(ids))
        objs = session.exec(stmt).all()
        cache[rel_model] = {getattr(obj, pk_attr_name): obj for obj in objs}

    # 注入字段
    for d in item_dicts:
        for field, (
            rel_model,
            pk_attr_name,
            target_attr,
            alias,
        ) in relation_map.items():
            rid = d.get(field)
            if rid is not None and rel_model in cache and rid in cache[rel_model]:
                obj = cache[rel_model][rid]
                d[alias] = getattr(obj, target_attr, None)
            else:
                d[alias] = None

    return item_dicts


def get_admins_count(session: Session) -> int:
    """获取管理员数量"""
    return session.exec(select(func.count(Admin.admin_id))).one()


# =======================
# 🌐 依赖项
# =======================


def check_login(token: str, session: Session = Depends(db_manager.get_session)):
    login_records = session.exec(
        select(Login).where(Login.token == token).order_by(Login.login_id.desc())
    ).all()
    # 找到第一个can_be_used为true的记录
    login_record = next(
        (record for record in login_records if record.can_be_used), None
    )

    if not login_record:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not login_record.can_be_used:
        raise HTTPException(status_code=401, detail="Token is disabled")
    return {
        "role": login_record.user_role,
        "id": login_record.user_id,
        "name": login_record.user_name,
    }


def logout(token: str, session: Session = Depends(db_manager.get_session)):
    # 将对应token的登录记录标记为不可用（使用与check_login相同的逻辑）
    login_records = session.exec(
        select(Login).where(Login.token == token).order_by(Login.login_id.desc())
    ).all()
    login_record = next(
        (record for record in login_records if record.can_be_used), None
    )

    if not login_record:
        raise HTTPException(status_code=401, detail="Invalid token")

    login_record.can_be_used = False
    session.add(login_record)
    session.commit()
    return {"message": "Successfully logged out"}


# =======================
# 📡 API 路由
# =======================


@app.get("/", summary="健康检查")
async def root():
    if get_admins_count(db_manager.get_session()) == 0:
        return {"status": "unhealthy", "message": "No admin found"}
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# --- 学生 ---
@app.get("/students", response_model=PaginatedResponse, summary="分页获取学生列表")
def read_students(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(db_manager.get_session),
):
    obj = check_login(token, session)

    # 只允许审核员和教师查看学生列表
    if obj["role"] == "student":
        raise HTTPException(status_code=403, detail="Permission denied")

    # 构建查询条件
    query = select(Student)

    # 如果是审核员，只显示该审核员负责的学生
    if obj["role"] == "reviewer":
        query = query.where(Student.reviewer_id == obj["id"])

    # 应用分页
    offset = (page - 1) * page_size
    students = session.exec(query.offset(offset).limit(page_size)).all()

    # 计算总数
    pk_col = list(Student.__table__.primary_key.columns)[0]
    total_stmt = select(func.count(pk_col))
    if obj["role"] == "reviewer":
        total_stmt = total_stmt.where(Student.reviewer_id == obj["id"])
    total = session.exec(total_stmt).one()

    total_pages = (total + page_size - 1) // page_size

    items = inject_relations(
        session,
        students,
        {"reviewer_id": (Reviewer, "reviewer_id", "name", "reviewer_name")},
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/students/count")
def students_count(token: str, session: Session = Depends(db_manager.get_session)):
    obj = check_login(token, session)
    if obj["role"] == "admin":
        count = session.exec(select(func.count(Student.student_id))).one()
        return {"students_count": count}
    elif obj["role"] in ["teacher", "student"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    else:
        # 修复：正确计算该审核员下的学生数量
        count = session.exec(
            select(func.count(Student.student_id)).where(
                Student.reviewer_id == obj["id"]
            )
        ).one()
        return {"students_count": count}


@app.get("/students/{student_id}", response_model=Student)
def read_student(
    token: str, student_id: int, session: Session = Depends(db_manager.get_session)
):
    obj = check_login(token, session)
    if obj["role"] == "student":
        if obj["id"] != student_id:
            raise HTTPException(status_code=403, detail="Permission denied")
        else:
            return get_by_id(session, Student, student_id, "student_id")
    return get_by_id(session, Student, student_id, "student_id")


@app.post("/students", response_model=Student, summary="创建学生")
def create_student_endpoint(
    token: str,
    student_data: StudentCreate,
    session: Session = Depends(db_manager.get_session),
):
    obj = check_login(token, session)
    if obj["role"] not in ["reviewer", "admin"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    student = Student(
        **student_data.model_dump(exclude={"guarantee_permission"}),
        guarantee_permission=student_data.guarantee_permission,
    )
    if student.password:
        student.password = hash_password(student.password)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


# --- 教师 ---
@app.get("/teachers", response_model=PaginatedResponse)
def read_teachers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(db_manager.get_session),
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
def teachers_count(session: Session = Depends(db_manager.get_session)):
    return {
        "teachers_count": session.exec(select(func.count(Teacher.teacher_id))).one()
    }


@app.get("/teachers/{teacher_id}", response_model=Teacher)
def read_teacher(teacher_id: int, session: Session = Depends(db_manager.get_session)):
    return get_by_id(session, Teacher, teacher_id, "teacher_id")


@app.post("/teachers", response_model=Teacher, summary="创建教师")
def create_teacher_endpoint(
    teacher_data: TeacherCreate,
    session: Session = Depends(db_manager.get_session),
):
    teacher = Teacher(**teacher_data.model_dump())
    if teacher.password:
        teacher.password = hash_password(teacher.password)
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


# --- 课程 ---
@app.get("/courses", response_model=PaginatedResponse)
def read_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(db_manager.get_session),
):
    courses, total, total_pages = paginate_query(session, Course, page, page_size)
    items = inject_relations(
        session,
        courses,
        {"teacher_id": (Teacher, "teacher_id", "name", "teacher_name")},
    )
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get(
    "/courses/count",
)
def courses_count(session: Session = Depends(db_manager.get_session)):
    return {"courses_count": session.exec(select(func.count(Course.course_id))).one()}


@app.get("/courses/{course_id}", response_model=Course)
def read_course(course_id: int, session: Session = Depends(db_manager.get_session)):
    return get_by_id(session, Course, course_id, "course_id")


@app.post("/courses", response_model=Course)
def create_course_endpoint(
    course: Course, session: Session = Depends(db_manager.get_session)
):
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


# --- 审核员 ---
@app.get("/reviewers", response_model=PaginatedResponse)
def read_reviewers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(db_manager.get_session),
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
def reviewers_count(session: Session = Depends(db_manager.get_session)):
    return {
        "reviewers_count": session.exec(select(func.count(Reviewer.reviewer_id))).one()
    }


@app.get("/reviewers/{reviewer_id}", response_model=Reviewer)
def read_reviewer(reviewer_id: int, session: Session = Depends(db_manager.get_session)):
    return get_by_id(session, Reviewer, reviewer_id, "reviewer_id")


@app.post("/reviewers", response_model=Reviewer, summary="创建审核员")
def create_reviewer_endpoint(
    reviewer_data: ReviewerCreate,
    session: Session = Depends(db_manager.get_session),
):
    reviewer = Reviewer(**reviewer_data.model_dump())
    if reviewer.password:
        reviewer.password = hash_password(reviewer.password)
    session.add(reviewer)
    session.commit()
    session.refresh(reviewer)
    return reviewer


# --- 请假记录 ---
@app.get("/leaves", response_model=PaginatedResponse)
def read_leaves(
    token: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(db_manager.get_session),
):
    # 验证登录状态并获取用户信息
    obj = check_login(token, session)

    # 构建基础查询
    query = select(Leave)

    # 如果是审核员，只显示该审核员负责的请假条
    if obj["role"] == "reviewer":
        query = query.where(Leave.reviewer_id == obj["id"])

    # 应用分页
    offset = (page - 1) * page_size
    leaves = session.exec(query.offset(offset).limit(page_size)).all()

    # 计算总数
    pk_col = list(Leave.__table__.primary_key.columns)[0]
    total_stmt = select(func.count(pk_col))
    if obj["role"] == "reviewer":
        total_stmt = total_stmt.where(Leave.reviewer_id == obj["id"])
    total = session.exec(total_stmt).one()

    total_pages = (total + page_size - 1) // page_size

    items = inject_relations(
        session,
        leaves,
        {
            "student_id": (Student, "student_id", "name", "student_name"),
            "reviewer_id": (Reviewer, "reviewer_id", "name", "reviewer_name"),
            "teacher_id": (Teacher, "teacher_id", "name", "teacher_name"),
            "guarantee_student_id": (
                Student,
                "student_id",
                "name",
                "guarantee_student_name",
            ),
        },
    )
    # 补充 course_name
    course_ids = {item["course_id"] for item in items if item.get("course_id")}
    if course_ids:
        courses = session.exec(
            select(Course).where(Course.course_id.in_(course_ids))
        ).all()
        course_map = {c.course_id: c.course_name for c in courses}
        for item in items:
            item["course_name"] = course_map.get(item.get("course_id"))
    else:
        for item in items:
            item["course_name"] = None
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/leaves/count")
def leaves_count(token: str, session: Session = Depends(db_manager.get_session)):
    obj = check_login(token, session)
    if obj["role"] == "admin":
        count = session.exec(select(func.count(Leave.leave_id))).one()
    elif obj["role"] in ["teacher", "student"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    else:
        count = session.exec(
            select(func.count(Leave.leave_id)).where(Leave.reviewer_id == obj["id"])
        ).one()

    return {"leaves_count": count}


@app.post("/leaves", response_model=Leave)
def create_leave_endpoint(
    leave_data: LeaveCreate,
    session: Session = Depends(db_manager.get_session),
):
    leave = Leave(**leave_data.model_dump())
    session.add(leave)
    session.commit()
    session.refresh(leave)
    return leave


@app.get("/leaves/student/{student_id}", response_model=List[Leave])
def read_leaves_by_student(
    student_id: int, session: Session = Depends(db_manager.get_session)
):
    return session.exec(select(Leave).where(Leave.student_id == student_id)).all()


@app.get("/leaves/reviewer/{reviewer_id}", response_model=List[Leave])
def read_leaves_by_reviewer(
    reviewer_id: int, session: Session = Depends(db_manager.get_session)
):
    return session.exec(select(Leave).where(Leave.reviewer_id == reviewer_id)).all()


@app.get("/leaves/course/{course_id}", response_model=List[Leave])
def read_leaves_by_course(
    course_id: int, session: Session = Depends(db_manager.get_session)
):
    return session.exec(select(Leave).where(Leave.course_id == course_id)).all()


@app.get("/leaves/teacher/{teacher_id}", response_model=List[Leave])
def read_leaves_by_teacher(
    teacher_id: int, session: Session = Depends(db_manager.get_session)
):
    course_ids = session.exec(
        select(Course.course_id).where(Course.teacher_id == teacher_id)
    ).all()
    if not course_ids:
        return []
    return session.exec(select(Leave).where(Leave.course_id.in_(course_ids))).all()


# --- 🔐 登录  ---
@app.post("/login", summary="登录")
def login(user: UserLogin, session: Session = Depends(db_manager.get_session)):
    role_model_map = {
        "teacher": (Teacher, "teacher_id"),
        "student": (Student, "student_id"),
        "reviewer": (Reviewer, "reviewer_id"),
        "admin": (Admin, "admin_id"),
    }
    if user.role not in role_model_map:
        raise HTTPException(400, "Invalid role")

    model_cls, id_field = role_model_map[user.role]
    obj = get_by_id(session, model_cls, user.id, id_field)

    if not obj.password:
        raise HTTPException(401, "User has no password set")

    if not verify_password(user.password, obj.password):
        raise HTTPException(401, "Invalid credentials")

    login_record = Login(
        user_role=user.role,
        user_id=user.id,
        user_name=obj.name,
        token=user.token,
    )
    session.add(login_record)
    session.commit()

    return {
        "role": user.role,
        "id": user.id,
        "name": obj.name,
        "token": user.token,  # 返回 token，前端需保存
    }


@app.get("/login/check")
def login_check(token: str, session: Session = Depends(db_manager.get_session)):
    """检查登录状态"""
    return check_login(token, session)


@app.get("/logout")
def log_out(token: str, session: Session = Depends(db_manager.get_session)):
    return logout(token, session)


@app.get("/login/orcode")
def login_qrcode(
    token: str,
    login_token: str,
    session_check: Session = Depends(
        db_manager.get_session,
    ),
    session_login: Session = Depends(db_manager.get_session),
):
    obj = check_login(token, session_check)
    if "detail" not in obj:
        login_record = Login(
            user_role=obj["role"],
            user_id=obj["id"],
            user_name=obj["name"],
            token=login_token,
        )
        session_login.add(login_record)
        session_login.commit()
        return {
            "role": obj["role"],
            "id": obj["id"],
            "name": obj["name"],
            "token": login_token,
        }


@app.post("/create/admin")
def create_admin(
    admin_data: AdminCreate,
    session: Session = Depends(db_manager.get_session),
):
    # 当管理员数为0时可用
    if get_admins_count(session) == 0:
        admin = Admin(**admin_data.model_dump())
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin
    else:
        raise HTTPException(status_code=400, detail="Admin already exists")
