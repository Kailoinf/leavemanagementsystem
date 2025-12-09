from sqlmodel import Session, select, func
from fastapi import HTTPException

from app.models import StudentCourse, Student, Course, Teacher
from app.schemas import StudentCourseCreate, StudentCourseResponse
from app.api.deps import check_login
from app.services.common import CommonService


class StudentCourseService:
    @staticmethod
    def create_student_course(
        token: str,
        student_course_data: StudentCourseCreate,
        session: Session,
    ):
        """学生选课"""
        obj = check_login(token, session)

        # 只有管理员和学生可以选课
        if obj["role"] not in ["admin", "student"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 如果是学生，只能给自己选课
        if obj["role"] == "student":
            student_course_data.student_id = obj["id"]

        # 验证学生是否存在
        student = session.exec(
            select(Student).where(Student.student_id == student_course_data.student_id)
        ).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # 验证课程是否存在
        course = session.exec(
            select(Course).where(Course.course_id == student_course_data.course_id)
        ).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # 检查是否已经选过该课程
        existing = session.exec(
            select(StudentCourse).where(
                StudentCourse.student_id == student_course_data.student_id,
                StudentCourse.course_id == student_course_data.course_id
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled in this course")

        student_course = StudentCourse(**student_course_data.model_dump())
        session.add(student_course)
        session.commit()
        session.refresh(student_course)
        return student_course

    @staticmethod
    def get_student_courses(
        token: str,
        student_id: int = None,
        session: Session = None,
    ):
        """获取学生的选课列表"""
        obj = check_login(token, session)

        # 权限检查
        if obj["role"] == "student":
            # 学生只能查看自己的选课
            student_id = obj["id"]
        elif obj["role"] in ["admin", "reviewer", "teacher"]:
            if not student_id:
                raise HTTPException(status_code=400, detail="student_id is required")
        else:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 查询选课记录
        courses = session.exec(
            select(StudentCourse).where(StudentCourse.student_id == student_id)
        ).all()

        # 补充关联信息
        items = CommonService.inject_relations(
            session,
            courses,
            {
                "student_id": (Student, "student_id", "student_name", "student_name"),
                "course_id": (Course, "course_id", "course_name", "course_name"),
            },
        )

        # 补充teacher_name
        course_ids = {item["course_id"] for item in items if item.get("course_id")}
        if course_ids:
            courses_info = session.exec(
                select(Course).where(Course.course_id.in_(course_ids))
            ).all()
            teacher_ids = {c.teacher_id for c in courses_info if c.teacher_id}

            if teacher_ids:
                teachers = session.exec(
                    select(Teacher).where(Teacher.teacher_id.in_(teacher_ids))
                ).all()
                teacher_map = {t.teacher_id: t.teacher_name for t in teachers}

                course_teacher_map = {c.course_id: c.teacher_id for c in courses_info}
                for item in items:
                    teacher_id = course_teacher_map.get(item.get("course_id"))
                    item["teacher_name"] = teacher_map.get(teacher_id) if teacher_id else None
            else:
                for item in items:
                    item["teacher_name"] = None
        else:
            for item in items:
                item["teacher_name"] = None

        return items

    @staticmethod
    def get_course_students(
        token: str,
        course_id: int,
        session: Session,
    ):
        """获取课程的学生列表"""
        obj = check_login(token, session)

        # 权限检查：管理员、教师、审核员可以查看课程学生
        if obj["role"] not in ["admin", "teacher", "reviewer"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 教师只能查看自己教授的课程
        if obj["role"] == "teacher":
            course = session.exec(
                select(Course).where(
                    Course.course_id == course_id,
                    Course.teacher_id == obj["id"]
                )
            ).first()
            if not course:
                raise HTTPException(status_code=403, detail="Not authorized to view this course's students")

        # 查询选该课程的学生
        enrollments = session.exec(
            select(StudentCourse).where(StudentCourse.course_id == course_id)
        ).all()

        # 补充学生信息和教师信息
        items = CommonService.inject_relations(
            session,
            enrollments,
            {
                "student_id": (Student, "student_id", "student_name", "student_name"),
                "course_id": (Course, "course_id", "course_name", "course_name"),
            },
        )

        # 补充 teacher_name
        course_info = session.exec(
            select(Course).where(Course.course_id == course_id)
        ).first()

        if course_info and course_info.teacher_id:
            teacher = session.exec(
                select(Teacher).where(Teacher.teacher_id == course_info.teacher_id)
            ).first()
            if teacher:
                for item in items:
                    item["teacher_name"] = teacher.teacher_name
            else:
                for item in items:
                    item["teacher_name"] = None
        else:
            for item in items:
                item["teacher_name"] = None

        return items

    @staticmethod
    def get_similar_course_students(
        token: str,
        teacher_id: int,
        course_id: int,
        session: Session,
    ):
        """获取同一教师下相似课程的学生列表（防止请错课程）"""
        obj = check_login(token, session)

        # 权限检查：管理员、教师、审核员可以查看
        if obj["role"] not in ["admin", "teacher", "reviewer"]:
            raise HTTPException(status_code=403, detail="Permission denied")

        # 教师只能查看自己的课程
        if obj["role"] == "teacher" and obj["id"] != teacher_id:
            raise HTTPException(status_code=403, detail="Not authorized to view other teacher's courses")

        # 获取当前课程信息
        current_course = session.exec(
            select(Course).where(Course.course_id == course_id)
        ).first()
        if not current_course:
            raise HTTPException(status_code=404, detail="Course not found")

        # 查找同一教师的所有课程（排除当前课程）
        similar_courses = session.exec(
            select(Course).where(
                Course.teacher_id == teacher_id,
                Course.course_id != course_id
            )
        ).all()

        # 获取所有相似课程的学生选课记录
        if not similar_courses:
            return []

        similar_course_ids = [c.course_id for c in similar_courses]
        enrollments = session.exec(
            select(StudentCourse).where(
                StudentCourse.course_id.in_(similar_course_ids),
                StudentCourse.status == "已选课"
            )
        ).all()

        # 补充关联信息
        items = CommonService.inject_relations(
            session,
            enrollments,
            {
                "student_id": (Student, "student_id", "student_name", "student_name"),
                "course_id": (Course, "course_id", "course_name", "course_name"),
            },
        )

        return items

    @staticmethod
    def verify_student_enrollment(
        student_id: int,
        course_id: int,
        session: Session,
    ) -> bool:
        """验证学生是否选择了某门课程"""
        enrollment = session.exec(
            select(StudentCourse).where(
                StudentCourse.student_id == student_id,
                StudentCourse.course_id == course_id,
                StudentCourse.status == "已选课"
            )
        ).first()
        return enrollment is not None