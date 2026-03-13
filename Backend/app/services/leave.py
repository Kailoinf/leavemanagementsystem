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
                "student_id": (Student, "student_id", "student_name", "student_name"),
                "reviewer_id": (Reviewer, "reviewer_id", "reviewer_name", "reviewer_name"),
                "teacher_id": (Teacher, "teacher_id", "teacher_name", "teacher_name"),
                "guarantee_student_id": (
                    Student,
                    "student_id",
                    "student_name",
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

        """根据学生ID获取请假记录（包含关联数据）"""
        leaves = session.exec(select(Leave).where(Leave.student_id == student_id)).all()

        # 注入关联数据
        items = CommonService.inject_relations(
            session,
            leaves,
            {
                "student_id": (Student, "student_id", "student_name", "student_name"),
                "reviewer_id": (Reviewer, "reviewer_id", "reviewer_name", "reviewer_name"),
                "teacher_id": (Teacher, "teacher_id", "teacher_name", "teacher_name"),
                "guarantee_student_id": (
                    Student,
                    "student_id",
                    "student_name",
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

        return items

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

    @staticmethod
    def edit_leave(
        token: str,
        leave_id: int,
        leave_data: LeaveCreate,
        session: Session,
    ):
        """编辑请假记录"""
        # 验证登录状态并获取用户信息
        obj = check_login(token, session)

        # 获取要编辑的请假记录
        leave = session.exec(
            select(Leave).where(Leave.leave_id == leave_id)
        ).first()

        if not leave:
            raise HTTPException(status_code=404, detail="Leave record not found")

        # 检查状态：已批准的记录无法修改
        if leave.status == "已批准":
            raise HTTPException(status_code=403, detail="Cannot edit approved leave request")

        # 权限验证
        if obj["role"] == "student":
            # 学生只能修改自己的记录
            if leave.student_id != obj["id"]:
                raise HTTPException(status_code=403, detail="Students can only edit their own leave requests")
        elif obj["role"] == "reviewer":
            # 审核员只能修改自己名下学生的记录
            if leave.reviewer_id != obj["id"]:
                raise HTTPException(status_code=403, detail="Reviewers can only edit leave requests of their assigned students")
        elif obj["role"] == "admin":
            # 管理员可以修改所有记录
            pass
        else:
            # 其他角色无权限修改
            raise HTTPException(status_code=403, detail="Permission denied")

        # 更新请假记录
        update_data = leave_data.model_dump(exclude_unset=True)

        # 不允许修改student_id，如果提供了不同的student_id，使用原来的ID
        if "student_id" in update_data:
            if update_data["student_id"] != leave.student_id:
                # 强制使用原来的student_id
                update_data["student_id"] = leave.student_id

        # 如果提供了course_id，需要验证学生是否选择了该课程
        if "course_id" in update_data and update_data["course_id"]:
            # 使用当前记录的student_id进行验证
            if not StudentCourseService.verify_student_enrollment(
                leave.student_id,
                update_data["course_id"],
                session
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Student has not enrolled in this course"
                )

        # 标记为已修改（改为布尔类型）
        update_data["is_modified"] = True

        # 应用更新
        for key, value in update_data.items():
            setattr(leave, key, value)

        session.commit()
        session.refresh(leave)
        return leave

    @staticmethod
    def approve_leave(
        token: str,
        leave_id: int,
        reviewer_note: str = None,
        session: Session = None,
    ):
        """审核通过请假申请"""
        # 验证登录状态并获取用户信息
        obj = check_login(token, session)

        # 只有审核员和管理员可以审核
        if obj["role"] not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Only reviewers and admins can approve leave requests")

        # 获取请假记录
        leave = session.exec(
            select(Leave).where(Leave.leave_id == leave_id)
        ).first()

        if not leave:
            raise HTTPException(status_code=404, detail="Leave record not found")

        # 检查状态
        if leave.status == "已批准":
            raise HTTPException(status_code=400, detail="Leave request has already been approved")
        if leave.status == "已拒绝":
            raise HTTPException(status_code=400, detail="Cannot approve a rejected leave request")

        # 权限验证：审核员只能审核分配给自己的请假记录
        if obj["role"] == "reviewer":
            if leave.reviewer_id != obj["id"]:
                raise HTTPException(status_code=403, detail="Reviewers can only approve leave requests assigned to them")

        # 审核权限分级验证
        leave_days = leave.leave_days
        reviewer = session.exec(
            select(Reviewer).where(Reviewer.reviewer_id == obj["id"])
        ).first()

        if not reviewer:
            raise HTTPException(status_code=404, detail="Reviewer not found")

        # 根据天数和审核员身份进行权限验证
        if leave_days <= 1 and reviewer.reviewer_name not in ["辅导员"]:
            raise HTTPException(status_code=403, detail="Leave requests <= 1 day can only be approved by counselors")
        elif leave_days <= 3 and reviewer.reviewer_name not in ["辅导员", "院党总支副书记"]:
            raise HTTPException(status_code=403, detail="Leave requests <= 3 days can only be approved by counselors or vice party secretaries")
        elif leave_days <= 7 and reviewer.reviewer_name not in ["辅导员", "院党总支副书记", "院党总支书记"]:
            raise HTTPException(status_code=403, detail="Leave requests <= 7 days can only be approved by counselors, vice party secretaries, or party secretaries")
        elif leave_days > 7 and reviewer.reviewer_name not in ["学生工作处"]:
            raise HTTPException(status_code=403, detail="Leave requests > 7 days can only be approved by student affairs office")

        # 更新状态
        leave.status = "已批准"
        leave.audit_remarks = reviewer_note
        leave.audit_time = datetime.now()

        session.commit()
        session.refresh(leave)
        return leave

    @staticmethod
    def reject_leave(
        token: str,
        leave_id: int,
        reviewer_note: str = None,
        session: Session = None,
    ):
        """拒绝请假申请"""
        # 验证登录状态并获取用户信息
        obj = check_login(token, session)

        # 只有审核员和管理员可以审核
        if obj["role"] not in ["reviewer", "admin"]:
            raise HTTPException(status_code=403, detail="Only reviewers and admins can reject leave requests")

        # 获取请假记录
        leave = session.exec(
            select(Leave).where(Leave.leave_id == leave_id)
        ).first()

        if not leave:
            raise HTTPException(status_code=404, detail="Leave record not found")

        # 检查状态
        if leave.status == "已拒绝":
            raise HTTPException(status_code=400, detail="Leave request has already been rejected")
        if leave.status == "已批准":
            raise HTTPException(status_code=400, detail="Cannot reject an approved leave request")

        # 权限验证：审核员只能审核分配给自己的请假记录
        if obj["role"] == "reviewer":
            if leave.reviewer_id != obj["id"]:
                raise HTTPException(status_code=403, detail="Reviewers can only reject leave requests assigned to them")

        # 更新状态
        leave.status = "已拒绝"
        leave.reviewer_note = reviewer_note
        leave.review_time = datetime.now()

        session.commit()
        session.refresh(leave)
        return leave