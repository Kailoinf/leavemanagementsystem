#!/usr/bin/env python3
"""
插入测试数据的脚本
用于在LMS系统中创建测试数据
"""

import sys
import os
from datetime import datetime, timedelta
import random
from sqlmodel import Session # 只导入 Session，不直接导入 engine

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import ( # 导入 DatabaseManager 和其他模型
    DatabaseManager, # 用于创建引擎和会话
    Reviewer,
    Student,
    Teacher,
    Leave,
    Course,
    hash_password, # 导入密码哈希函数
)


def create_test_reviewers(session: Session):
    """创建测试审核员数据"""
    reviewers_data = [
        {
            "reviewer_id": 1001,
            "name": "张审核",
            "school": "学生处",
            "role": "处长",
            "password": "123456",
        },
        {
            "reviewer_id": 1002,
            "name": "李主任",
            "school": "教务处",
            "role": "主任",
            "password": "123456",
        },
        {
            "reviewer_id": 1003,
            "name": "王老师",
            "school": "计算机系",
            "role": "辅导员",
            "password": "123456",
        },
        {
            "reviewer_id": 1004,
            "name": "刘书记",
            "school": "团委",
            "role": "书记",
            "password": "123456",
        },
    ]

    created_reviewers = []
    for reviewer_data in reviewers_data:
        # 处理密码
        password_plain = reviewer_data.pop('password', None) # 从字典中取出密码
        reviewer = Reviewer(**reviewer_data) # 用剩余数据创建对象
        if password_plain:
            reviewer.password = hash_password(password_plain) # 哈希密码
            reviewer.password_is_hashed = True # 标记为已哈希
        else:
            reviewer.password_is_hashed = False # 没有密码则标记为False

        session.add(reviewer)
        created_reviewers.append(reviewer)
        print(f"创建审核员: {reviewer.name} (ID: {reviewer.reviewer_id})")

    session.commit() # 统一提交
    return created_reviewers


def create_test_teachers(session: Session):
    """创建测试教师数据"""
    teachers_data = [
        {"teacher_id": 2001, "name": "陈教授", "password": "123456"},
        {"teacher_id": 2002, "name": "赵副教授", "password": "123456"},
        {"teacher_id": 2003, "name": "孙讲师", "password": "123456"},
        {"teacher_id": 2004, "name": "周助教", "password": "123456"},
    ]

    created_teachers = []
    for teacher_data in teachers_data:
        # 处理密码
        password_plain = teacher_data.pop('password', None)
        teacher = Teacher(**teacher_data)
        if password_plain:
            teacher.password = hash_password(password_plain)
            teacher.password_is_hashed = True
        else:
            teacher.password_is_hashed = False

        session.add(teacher)
        created_teachers.append(teacher)
        print(f"创建教师: {teacher.name} (ID: {teacher.teacher_id})")

    session.commit()
    return created_teachers


def create_test_courses(session: Session, teachers):
    """创建测试课程数据"""
    courses_data = [
        {
            "course_id": 3001,
            "teacher_id": teachers[0].teacher_id,
            "course_name": "数据结构",
            "class_hours": "64",
        },
        {
            "course_id": 3002,
            "teacher_id": teachers[0].teacher_id,
            "course_name": "算法分析",
            "class_hours": "48",
        },
        {
            "course_id": 3003,
            "teacher_id": teachers[1].teacher_id,
            "course_name": "数据库原理",
            "class_hours": "56",
        },
        {
            "course_id": 3004,
            "teacher_id": teachers[1].teacher_id,
            "course_name": "软件工程",
            "class_hours": "48",
        },
        {
            "course_id": 3005,
            "teacher_id": teachers[2].teacher_id,
            "course_name": "计算机网络",
            "class_hours": "64",
        },
        {
            "course_id": 3006,
            "teacher_id": teachers[2].teacher_id,
            "course_name": "操作系统",
            "class_hours": "56",
        },
        {
            "course_id": 3007,
            "teacher_id": teachers[3].teacher_id,
            "course_name": "Web开发",
            "class_hours": "48",
        },
        {
            "course_id": 3008,
            "teacher_id": teachers[3].teacher_id,
            "course_name": "移动应用开发",
            "class_hours": "48",
        },
    ]

    created_courses = []
    for course_data in courses_data:
        course = Course(**course_data)
        session.add(course)
        created_courses.append(course)
        print(f"创建课程: {course.course_name} (ID: {course.course_id})")

    session.commit()
    return created_courses


def create_test_students(session: Session, reviewers):
    """创建测试学生数据"""
    schools = ["信息工程学院", "马克思主义学院", "智能制造学院", "会计学院", "体育学院"]

    created_students = []
    for i in range(1, 51):  # 创建50个学生
        student_data = {
            "student_id": 4000 + i,
            "name": f"学生{i:02d}",
            "password": "123456",
            "school": random.choice(schools),
            "reviewer_id": random.choice(reviewers).reviewer_id,
            # guarantee_permission 已经是 datetime 对象，无需转换
            "guarantee_permission": datetime.now() + timedelta(days=random.randint(1, 365)),
        }
        # 处理密码
        password_plain = student_data.pop('password', None)
        student = Student(**student_data)
        if password_plain:
            student.password = hash_password(password_plain)
            student.password_is_hashed = True
        else:
            student.password_is_hashed = False

        session.add(student)
        created_students.append(student)
        print(f"创建学生: {student.name} (学号: {student.student_id})")

    session.commit()
    return created_students


def create_test_leaves(session: Session, students, courses, reviewers):
    """创建测试请假记录数据"""
    leave_types = ["事假", "病假", "公假", "婚假", "丧假"]
    status_types = ["待审批", "已批准", "已拒绝", "已撤销"]

    created_leaves = []
    leave_id_counter = 5001

    for i, student in enumerate(students[:30]):  # 为前30个学生创建请假记录
        num_leaves = random.randint(1, 3)  # 每个学生1-3条请假记录

        for j in range(num_leaves):
            leave_date = datetime.now() - timedelta(days=random.randint(1, 90))
            leave_days = random.randint(1, 7)

            leave_data = {
                "leave_id": leave_id_counter,
                "student_id": student.student_id,
                "leave_date": leave_date,
                "class_hours": f"{random.randint(1, 8)}",
                "leave_days": str(leave_days),
                "status": random.choice(status_types),
                "leave_type": random.choice(leave_types),
                "remarks": f"学生{student.name}的第{j + 1}次请假申请",
                "materials": "请假条.png" if random.random() > 0.5 else None,
                "reviewer_id": random.choice(reviewers).reviewer_id,
                "teacher_id": random.choice(courses).teacher_id,
                "audit_remarks": "审核通过" if random.random() > 0.3 else "需要补充材料",
                "audit_time": leave_date + timedelta(hours=random.randint(1, 24)),
                "course_id": random.choice(courses).course_id,
                "is_modified": "否",
                "guarantee_student_id": random.choice(students).student_id if random.random() > 0.7 else None,
            }

            leave = Leave(**leave_data)
            session.add(leave)
            created_leaves.append(leave)
            print(
                f"创建请假记录: 学生{student.name} - {leave.leave_type} {leave.leave_days}天 (ID: {leave.leave_id})"
            )

            leave_id_counter += 1

    session.commit()
    return created_leaves


def clear_all_data(session: Session):
    """清空所有测试数据"""
    print("正在清空现有数据...")

    # 按依赖关系顺序删除数据 (外键依赖关系)
    # Leave 依赖 Student, Reviewer, Teacher, Course
    session.exec(Leave.__table__.delete())
    # Course 依赖 Teacher
    session.exec(Course.__table__.delete())
    # Student 依赖 Reviewer
    session.exec(Student.__table__.delete())
    session.exec(Teacher.__table__.delete())
    session.exec(Reviewer.__table__.delete())

    session.commit()
    print("数据清空完成")


def main():
    """主函数"""
    print("开始创建测试数据...")

    # 创建 DatabaseManager 实例来管理数据库连接
    db_manager = DatabaseManager()

    # 使用 db_manager 获取会话
    with Session(db_manager.engine) as session:
        # 询问是否清空现有数据
        clear_data = input("是否清空现有数据? (y/N): ").lower().strip()
        if clear_data == "y":
            clear_all_data(session)

        # 创建测试数据
        print("\n1. 创建审核员...")
        reviewers = create_test_reviewers(session)

        print("\n2. 创建教师...")
        teachers = create_test_teachers(session)

        print("\n3. 创建课程...")
        courses = create_test_courses(session, teachers)

        print("\n4. 创建学生...")
        students = create_test_students(session, reviewers)

        print("\n5. 创建请假记录...")
        leaves = create_test_leaves(session, students, courses, reviewers)

        print(f"\n测试数据创建完成!")
        print(f"- 审核员: {len(reviewers)} 个")
        print(f"- 教师: {len(teachers)} 个")
        print(f"- 课程: {len(courses)} 个")
        print(f"- 学生: {len(students)} 个")
        print(f"- 请假记录: {len(leaves)} 条")


if __name__ == "__main__":
    main()