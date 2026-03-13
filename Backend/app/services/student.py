from sqlmodel import Session, select, func
from fastapi import Depends, HTTPException, Query

from app.models import Student, Reviewer, School
from app.schemas import StudentCreate
from app.api.deps import check_login
from app.services.common import CommonService
from app.utils.password import hash_password


class StudentService:
    @staticmethod
    def get_students(
        token: str,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        session: Session = Depends(lambda: None),
    ):
        """分页获取学生列表"""
        obj = check_login(token, session)

        # 只允许审核员查看全部学生列表
        if obj["role"] == "teacher":
            raise HTTPException(status_code=403, detail="Permission denied")

        # 构建查询条件
        query = select(Student)

        # 如果是审核员，只显示该审核员负责的学生
        if obj["role"] == "reviewer":
            query = query.where(Student.reviewer_id == obj["id"])

        elif obj["role"] == "student":
            query = query.where(Student.student_id == obj["id"])

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

        items = CommonService.inject_relations(
            session,
            students,
            {
                "reviewer_id": (
                    Reviewer,
                    "reviewer_id",
                    "reviewer_name",
                    "reviewer_name",
                ),
                "school_id": (
                    School,
                    "school_id",
                    "school_name",
                    "school_name",
                )
            },
        )
        return items, total, total_pages

    @staticmethod
    def get_students_count(token: str, session: Session):
        """获取学生数量"""
        obj = check_login(token, session)
        if obj["role"] == "admin":
            count = session.exec(select(func.count(Student.student_id))).one()
            return {"students_count": count}
        elif obj["role"] == "teacher":
            raise HTTPException(status_code=403, detail="Permission denied")
        elif obj["role"] == "student":
            return {"students_count": "自己"}
        else:
            # 修复：正确计算该审核员下的学生数量
            count = session.exec(
                select(func.count(Student.student_id)).where(
                    Student.reviewer_id == obj["id"]
                )
            ).one()
            return {"students_count": count}

    @staticmethod
    def get_student_by_id(token: str, student_id: int, session: Session):
        """根据ID获取学生"""
        obj = check_login(token, session)
        if obj["role"] == "student":
            if obj["id"] != student_id:
                raise HTTPException(status_code=403, detail="Permission denied")
            else:
                return CommonService.get_by_id(
                    session, Student, student_id, "student_id"
                )
        return CommonService.get_by_id(session, Student, student_id, "student_id")

    @staticmethod
    def create_student(
        token: str,
        student_data: StudentCreate,
        session: Session,
    ):
        """创建学生"""
        obj = check_login(token, session)
        if obj["role"] not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        student = Student(**student_data.model_dump())
        if student.password:
            student.password = hash_password(student.password)
        session.add(student)
        session.commit()
        session.refresh(student)
        return student
