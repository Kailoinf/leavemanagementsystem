"""批量导入API"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.database.connection import get_session
from app.services.import_service import ImportService
from app.api.deps import check_login

router = APIRouter()


@router.post("/import/students")
async def import_students(
    file: UploadFile = File(...),
    default_password: str = "123456",
    session: Session = Depends(get_session),
):
    """
    批量导入学生

    - **file**: CSV文件，必须包含列：学号,姓名,学院,班级,专业,辅导员ID
    - **default_password**: 默认密码，默认为"123456"
    """
    # 验证文件
    ImportService.validate_csv_file(file)

    # 解析CSV
    csv_data = await ImportService.parse_csv(file)

    # 导入数据
    result = ImportService.import_students(csv_data, session, default_password)

    return {
        "message": f"成功导入 {result['success_count']} 条记录",
        "result": result
    }


@router.post("/import/teachers")
async def import_teachers(
    file: UploadFile = File(...),
    default_password: str = "123456",
    session: Session = Depends(get_session),
):
    """
    批量导入教师

    - **file**: CSV文件，必须包含列：工号,姓名,部门,职称
    - **default_password**: 默认密码，默认为"123456"
    """
    # 验证文件
    ImportService.validate_csv_file(file)

    # 解析CSV
    csv_data = await ImportService.parse_csv(file)

    # 导入数据
    result = ImportService.import_teachers(csv_data, session, default_password)

    return {
        "message": f"成功导入 {result['success_count']} 条记录",
        "result": result
    }


@router.post("/import/reviewers")
async def import_reviewers(
    file: UploadFile = File(...),
    default_password: str = "123456",
    session: Session = Depends(get_session),
):
    """
    批量导入审核员

    - **file**: CSV文件，必须包含列：工号,姓名,学院,审核员身份
    - **default_password**: 默认密码，默认为"123456"

    审核员身份必须是：辅导员, 院党总支副书记, 院党总支书记, 学生工作处
    """
    # 验证文件
    ImportService.validate_csv_file(file)

    # 解析CSV
    csv_data = await ImportService.parse_csv(file)

    # 导入数据
    result = ImportService.import_reviewers(csv_data, session, default_password)

    return {
        "message": f"成功导入 {result['success_count']} 条记录",
        "result": result
    }


@router.get("/import/template/{role}")
async def download_template(role: str):
    """
    下载导入模板

    - **role**: 角色，可选值：student, teacher, reviewer
    """
    template = ImportService.get_template(role)

    if not template:
        raise HTTPException(status_code=400, detail="无效的角色类型")

    filename = f"{role}_import_template.csv"
    output = BytesIO()
    output.write(template.encode('utf-8-sig'))  # 使用BOM以支持Excel正确打开
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
