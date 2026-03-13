"""文件上传API"""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session

from app.database.connection import get_session
from app.services.file import FileService
from app.api.deps import check_login

router = APIRouter()


@router.post("/upload/material/{leave_id}")
async def upload_material(
    leave_id: int,
    token: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """
    上传请假材料

    - **leave_id**: 请假记录ID
    - **file**: 上传的文件（支持PDF、JPG、PNG、DOC、DOCX）
    - **max_size**: 最大10MB
    """
    # 验证登录状态
    obj = check_login(token, session)

    # 验证用户权限（只有学生和审核员可以上传材料）
    if obj["role"] not in ["student", "reviewer", "admin"]:
        raise Exception("Permission denied")

    result = await FileService.upload_material(file, leave_id)
    return result


@router.delete("/files/material/{filename}")
def delete_material(
    filename: str,
    token: str,
    session: Session = Depends(get_session),
):
    """删除材料文件"""
    # 验证登录状态
    obj = check_login(token, session)

    # 只有管理员可以删除文件
    if obj["role"] != "admin":
        raise Exception("Permission denied")

    success = FileService.delete_material(filename)
    return {"success": success, "message": "文件删除成功" if success else "文件不存在"}
