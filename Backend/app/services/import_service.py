"""批量导入服务"""
import csv
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from sqlmodel import Session
import hashlib

from app.models import Student, Teacher, Reviewer, Admin
from app.utils.password import hash_password


class ImportService:
    """批量导入管理服务"""

    @staticmethod
    def validate_csv_file(file: UploadFile) -> bool:
        """验证CSV文件格式"""
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="文件必须是CSV格式")
        return True

    @staticmethod
    async def parse_csv(file: UploadFile) -> List[Dict[str, Any]]:
        """解析CSV文件"""
        content = await file.read()
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5']

        for encoding in encodings:
            try:
                decoded_content = content.decode(encoding)
                reader = csv.DictReader(decoded_content.splitlines())
                data = list(reader)
                if data:
                    return data
            except UnicodeDecodeError:
                continue

        raise HTTPException(status_code=400, detail="无法解析CSV文件，请检查文件编码")

    @staticmethod
    def import_students(
        csv_data: List[Dict[str, Any]],
        session: Session,
        default_password: str = "123456"
    ) -> Dict[str, Any]:
        """批量导入学生"""
        success_count = 0
        error_count = 0
        errors = []

        for row_num, row in enumerate(csv_data, 1):
            try:
                # 验证必要字段
                if not row.get('学号') or not row.get('姓名'):
                    errors.append(f"第{row_num}行：缺少学号或姓名")
                    error_count += 1
                    continue

                # 检查是否已存在
                existing = session.exec(
                    select(Student).where(Student.student_id == int(row['学号']))
                ).first()

                if existing:
                    errors.append(f"第{row_num}行：学号 {row['学号']} 已存在")
                    error_count += 1
                    continue

                # 创建学生记录
                student = Student(
                    student_id=int(row['学号']),
                    student_name=row['姓名'],
                    password=hash_password(default_password),
                    college=row.get('学院', ''),
                    class_name=row.get('班级', ''),
                    major=row.get('专业', ''),
                    reviewer_id=int(row.get('辅导员ID', 0)) if row.get('辅导员ID') else None,
                    guarantee_permission=None  # 默认无担保权限
                )

                session.add(student)
                success_count += 1

            except ValueError as e:
                errors.append(f"第{row_num}行：数据格式错误 - {str(e)}")
                error_count += 1
            except Exception as e:
                errors.append(f"第{row_num}行：导入失败 - {str(e)}")
                error_count += 1

        # 提交成功记录
        if success_count > 0:
            session.commit()

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]  # 只返回前10个错误
        }

    @staticmethod
    def import_teachers(
        csv_data: List[Dict[str, Any]],
        session: Session,
        default_password: str = "123456"
    ) -> Dict[str, Any]:
        """批量导入教师"""
        success_count = 0
        error_count = 0
        errors = []

        for row_num, row in enumerate(csv_data, 1):
            try:
                # 验证必要字段
                if not row.get('工号') or not row.get('姓名'):
                    errors.append(f"第{row_num}行：缺少工号或姓名")
                    error_count += 1
                    continue

                # 检查是否已存在
                existing = session.exec(
                    select(Teacher).where(Teacher.teacher_id == int(row['工号']))
                ).first()

                if existing:
                    errors.append(f"第{row_num}行：工号 {row['工号']} 已存在")
                    error_count += 1
                    continue

                # 创建教师记录
                teacher = Teacher(
                    teacher_id=int(row['工号']),
                    teacher_name=row['姓名'],
                    password=hash_password(default_password),
                    department=row.get('部门', ''),
                    title=row.get('职称', '')
                )

                session.add(teacher)
                success_count += 1

            except ValueError as e:
                errors.append(f"第{row_num}行：数据格式错误 - {str(e)}")
                error_count += 1
            except Exception as e:
                errors.append(f"第{row_num}行：导入失败 - {str(e)}")
                error_count += 1

        # 提交成功记录
        if success_count > 0:
            session.commit()

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]
        }

    @staticmethod
    def import_reviewers(
        csv_data: List[Dict[str, Any]],
        session: Session,
        default_password: str = "123456"
    ) -> Dict[str, Any]:
        """批量导入审核员"""
        success_count = 0
        error_count = 0
        errors = []

        for row_num, row in enumerate(csv_data, 1):
            try:
                # 验证必要字段
                if not row.get('工号') or not row.get('姓名') or not row.get('审核员身份'):
                    errors.append(f"第{row_num}行：缺少工号、姓名或审核员身份")
                    error_count += 1
                    continue

                # 检查是否已存在
                existing = session.exec(
                    select(Reviewer).where(Reviewer.reviewer_id == int(row['工号']))
                ).first()

                if existing:
                    errors.append(f"第{row_num}行：工号 {row['工号']} 已存在")
                    error_count += 1
                    continue

                # 验证审核员身份
                valid_roles = ['辅导员', '院党总支副书记', '院党总支书记', '学生工作处']
                reviewer_name = row.get('审核员身份')
                if reviewer_name not in valid_roles:
                    errors.append(f"第{row_num}行：审核员身份必须是 {', '.join(valid_roles)}")
                    error_count += 1
                    continue

                # 创建审核员记录
                reviewer = Reviewer(
                    reviewer_id=int(row['工号']),
                    reviewer_name=row.get('审核员身份', row['姓名']),  # 使用审核员身份作为名称
                    password=hash_password(default_password)
                )

                session.add(reviewer)
                success_count += 1

            except ValueError as e:
                errors.append(f"第{row_num}行：数据格式错误 - {str(e)}")
                error_count += 1
            except Exception as e:
                errors.append(f"第{row_num}行：导入失败 - {str(e)}")
                error_count += 1

        # 提交成功记录
        if success_count > 0:
            session.commit()

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]
        }

    @staticmethod
    def get_template(role: str) -> str:
        """获取导入模板CSV内容"""
        templates = {
            "student": "学号,姓名,学院,班级,专业,辅导员ID\n20240001,张三,计算机学院,计科1班,计算机科学,1\n20240002,李四,计算机学院,计科1班,计算机科学,1",
            "teacher": "工号,姓名,部门,职称\n1001,王老师,计算机学院,教授\n1002,李老师,计算机学院,副教授",
            "reviewer": "工号,姓名,学院,审核员身份\n1,辅导员1,计算机学院,辅导员\n2,副书记1,计算机学院,院党总支副书记\n3,书记1,计算机学院,院党总支书记\n4,学工处1,学生工作处,学生工作处"
        }

        return templates.get(role, "")
