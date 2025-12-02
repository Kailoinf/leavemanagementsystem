#!/usr/bin/env python3
"""
插入测试数据的脚本
用于在LMS系统中创建测试数据
"""

import sys
import os
from datetime import datetime, timedelta
import random
from sqlmodel import Session, select

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    engine,
    Reviewer,
    Student,
    Teacher,
    Leave,
    Course,
    create_reviewer,
    create_student,
    create_leave,
)


def create_test_reviewers(session: Session):
    """创建测试审核员数据"""
    reviewers_data = [
        {
            "reviewer_id": 1001,
            "name": "张审核",
            "department": "学生处",
            "role": "处长",
            "password": "123456",
        },
        {
            "reviewer_id": 1002,
            "name": "李主任",
            "department": "教务处",
            "role": "主任",
            "password": "123456",
        },
        {
            "reviewer_id": 1003,
            "name": "王老师",
            "department": "计算机系",
            "role": "辅导员",
            "password": "123456",
        },
        {
            "reviewer_id": 1004,
            "name": "刘书记",
            "department": "团委",
            "role": "书记",
            "password": "123456",
        },
    ]

    created_reviewers = []
    for reviewer_data in reviewers_data:
        reviewer = Reviewer(**reviewer_data)
        created_reviewer = create_reviewer(session, reviewer)
        created_reviewers.append(created_reviewer)
        print(f"创建审核员: {created_reviewer.name}")

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
        teacher = Teacher(**teacher_data)
        session.add(teacher)
        created_teachers.append(teacher)
        print(f"创建教师: {teacher.name}")

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
        print(f"创建课程: {course.course_name}")

    session.commit()
    return created_courses


def create_test_students(session: Session, reviewers):
    """创建测试学生数据"""
    departments = ["计算机系", "软件工程", "电子信息", "自动化", "数学系"]

    created_students = []
    for i in range(1, 51):  # 创建50个学生
        student_data = {
            "student_id": 4000 + i,
            "name": f"学生{i:02d}",
            "password": "123456",
            "department": random.choice(departments),
            "reviewer_id": random.choice(reviewers).reviewer_id,
            "guarantee_permission": datetime.now()
            + timedelta(days=random.randint(1, 365)),
        }
        student = Student(**student_data)
        created_student = create_student(session, student)
        created_students.append(created_student)
        print(f"创建学生: {created_student.name} (学号: {created_student.student_id})")

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
                "audit_remarks": "审核通过"
                if random.random() > 0.3
                else "需要补充材料",
                "audit_time": leave_date + timedelta(hours=random.randint(1, 24)),
                "course_id": random.choice(courses).course_id,
                "is_modified": "否",
                "guarantee_student_id": random.choice(students).student_id
                if random.random() > 0.7
                else None,
            }

            leave = Leave(**leave_data)
            session.add(leave)
            created_leaves.append(leave)
            print(
                f"创建请假记录: 学生{student.name} - {leave.leave_type} {leave.leave_days}天"
            )

            leave_id_counter += 1

    session.commit()
    return created_leaves


def create_test_teacher(session: Session, teacher_data):
    """创建单个教师"""
    teacher = Teacher(**teacher_data)
    session.add(teacher)
    session.commit()
    session.refresh(teacher)
    return teacher


def create_test_course(session: Session, course_data):
    """创建单个课程"""
    course = Course(**course_data)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def create_test_leave(session: Session, leave_data):
    """创建单个请假记录"""
    leave = Leave(**leave_data)
    session.add(leave)
    session.commit()
    session.refresh(leave)
    return leave


def clear_all_data(session: Session):
    """清空所有测试数据"""
    print("正在清空现有数据...")

    # 按依赖关系顺序删除数据
    session.exec(Leave.__table__.delete())
    session.exec(Course.__table__.delete())
    session.exec(Student.__table__.delete())
    session.exec(Teacher.__table__.delete())
    session.exec(Reviewer.__table__.delete())

    session.commit()
    print("数据清空完成")


def main():
    """主函数"""
    print("开始创建测试数据...")

    with Session(engine) as session:
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
