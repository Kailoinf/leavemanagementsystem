from sqlmodel import Session, select, func
from fastapi import Depends, Query, HTTPException
from datetime import datetime

from app.models import Leave, Student, Reviewer, Teacher, Course
from app.services.student_course import StudentCourseService
from app.schemas import LeaveCreate
from app.api.deps import check_login
from app.services.common import CommonService


class LeaveService:
    @staticmethod
    def get_leaves(
        token: str,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        session: Session = Depends(lambda: None),
    ):
        """分页获取请假记录"""
        # 验证登录状态并获取用户信息
        obj = check_login(token, session)

        # 构建基础查询
        query = select(Leave)

        # 根据角色应用不同的过滤条件
        # 管理员：获取全部记录
        # 学生：只能获取自己的记录
        # 审核员：只能获取分配给自己的记录
        # 教师：只能获取自己教授课程的请假记录
        if obj["role"] == "student":
            query = query.where(Leave.student_id == obj["id"])
        elif obj["role"] == "reviewer":
            query = query.where(Leave.reviewer_id == obj["id"])
        elif obj["role"] == "teacher":
            # 获取教师教授的课程ID列表
            course_ids = session.exec(
                select(Course.course_id).where(Course.teacher_id == obj["id"])
            ).all()
            if course_ids:
                query = query.where(Leave.course_id.in_(course_ids))
            else:
                # 如果教师没有教授任何课程，则返回空结果
                query = query.where(Leave.course_id.is_(None))

        # 应用分页
        offset = (page - 1) * page_size
        leaves = session.exec(query.offset(offset).limit(page_size)).all()

        # 计算总数
        pk_col = list(Leave.__table__.primary_key.columns)[0]
        total_stmt = select(func.count(pk_col))
        if obj["role"] == "student":
            total_stmt = total_stmt.where(Leave.student_id == obj["id"])
        elif obj["role"] == "reviewer":
            total_stmt = total_stmt.where(Leave.reviewer_id == obj["id"])
        elif obj["role"] == "teacher":
            course_ids = session.exec(
                select(Course.course_id).where(Course.teacher_id == obj["id"])
            ).all()
            if course_ids:
                total_stmt = total_stmt.where(Leave.course_id.in_(course_ids))
            else:
                total_stmt = total_stmt.where(Leave.course_id.is_(None))
        total = session.exec(total_stmt).one()

        total_pages = (total + page_size - 1) // page_size

        items = CommonService.inject_relations(
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

        return items, total, total_pages

    @staticmethod
    def get_leaves_count(token: str, session: Session):
        """获取请假记录数量"""
        obj = check_login(token, session)
        if obj["role"] == "admin":
            count = session.exec(select(func.count(Leave.leave_id))).one()
        elif obj["role"] == "student":
            count = session.exec(
                select(func.count(Leave.leave_id)).where(Leave.student_id == obj["id"])
            ).one()
        elif obj["role"] == "reviewer":
            count = session.exec(
                select(func.count(Leave.leave_id)).where(Leave.reviewer_id == obj["id"])
            ).one()
        elif obj["role"] == "teacher":
            # 获取教师教授的课程ID列表
            course_ids = session.exec(
                select(Course.course_id).where(Course.teacher_id == obj["id"])
            ).all()
            if course_ids:
                count = session.exec(
                    select(func.count(Leave.leave_id)).where(Leave.course_id.in_(course_ids))
                ).one()
            else:
                count = 0
        else:
            raise HTTPException(status_code=403, detail="Permission denied")

        return {"leaves_count": count}

    @staticmethod
    def create_leave(
        token: str,
        leave_data: LeaveCreate,
        session: Session,
    ):
        obj = check_login(token, session)

        # 创建一个数据字典的副本来修改
        leave_dict = leave_data.model_dump()

        # 根据用户角色自动设置student_id
        if obj["role"] == "student":
            leave_dict["student_id"] = obj["id"]
        elif not leave_dict.get("student_id"):
            # 如果不是学生且没有提供student_id，抛出错误
            raise HTTPException(status_code=400, detail="student_id is required for non-student users")

        # 自动设置reviewer_id：根据学生的reviewer_id设置
        student = session.exec(
            select(Student).where(Student.student_id == leave_dict["student_id"])
        ).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        if student.reviewer_id:
            leave_dict["reviewer_id"] = student.reviewer_id
        else:
            raise HTTPException(status_code=400, detail="Student has no assigned reviewer")

        # 验证学生是否选择了该课程
        if leave_dict.get("course_id"):
            if not StudentCourseService.verify_student_enrollment(
                leave_dict["student_id"],
                leave_dict["course_id"],
                session
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Student has not enrolled in this course"
                )

        # 如果没有提供leave_date，自动设置为当前时间
        if not leave_dict.get("leave_date"):
            leave_dict["leave_date"] = datetime.now()

        leave = Leave(**leave_dict)
        session.add(leave)
        session.commit()
        session.refresh(leave)
        return leave

    @staticmethod
    def get_leaves_by_student(token: str, student_id: int, session: Session):
        obj = check_login(token, session)
        # 管理员和审核员可以查看任意学生的请假记录
        if obj["role"] in ["admin", "reviewer"]:
            pass
        # 学生只能查看自己的请假记录
        elif obj["role"] == "student":
            if obj["id"] != student_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        # 教师只能查看自己课程的学生请假记录
        elif obj["role"] == "teacher":
            # 检查该学生是否在教师教授的课程中
            course_ids = session.exec(
                select(Course.course_id).where(Course.teacher_id == obj["id"])
            ).all()
            if course_ids:
                student_in_courses = session.exec(
                    select(Leave.leave_id)
                    .where(Leave.student_id == student_id)
                    .where(Leave.course_id.in_(course_ids))
                ).first()
                if not student_in_courses:
                    raise HTTPException(status_code=403, detail="Permission denied")
            else:
                raise HTTPException(status_code=403, detail="Permission denied")
        """根据学生ID获取请假记录"""
        return session.exec(select(Leave).where(Leave.student_id == student_id)).all()

    @staticmethod
    def get_leaves_by_reviewer(token: str, reviewer_id: int, session: Session):
        obj = check_login(token, session)
        # 审核员只能查看分配给自己的请假记录
        if obj["role"] == "reviewer":
            if obj["id"] != reviewer_id:
                raise HTTPException(status_code=403, detail="Permission denied")
        # 管理员可以查看任意审核员的记录
        elif obj["role"] == "admin":
            pass
        # 其他角色无权限
        else:
            raise HTTPException(status_code=403, detail="Permission denied")
        """根据审核员ID获取请假记录"""
        return session.exec(select(Leave).where(Leave.reviewer_id == reviewer_id)).all()

    @staticmethod
    def get_leaves_by_course(course_id: int, session: Session):
        """根据课程ID获取请假记录"""
        return session.exec(select(Leave).where(Leave.course_id == course_id)).all()

    @staticmethod
    def get_leaves_by_teacher(teacher_id: int, session: Session):
        """根据教师ID获取请假记录"""
        course_ids = session.exec(
            select(Course.course_id).where(Course.teacher_id == teacher_id)
        ).all()
        if not course_ids:
            return []
        return session.exec(select(Leave).where(Leave.course_id.in_(course_ids))).all()