"""文件上传服务"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
import hashlib


class FileService:
    """文件上传管理服务"""

    # 上传目录
    UPLOAD_DIR = Path("uploads")
    MATERIALS_DIR = UPLOAD_DIR / "materials"

    @classmethod
    def ensure_directories(cls):
        """确保上传目录存在"""
        cls.MATERIALS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def generate_filename(cls, original_filename: str, leave_id: int) -> str:
        """生成唯一的文件名"""
        # 获取文件扩展名
        ext = Path(original_filename).suffix
        # 生成基于时间和leave_id的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 添加哈希值确保唯一性
        hash_part = hashlib.md5(f"{leave_id}_{timestamp}".encode()).hexdigest()[:8]
        return f"leave_{leave_id}_{hash_part}_{timestamp}{ext}"

    @classmethod
    async def upload_material(
        cls,
        file: UploadFile,
        leave_id: int,
        max_size: int = 10 * 1024 * 1024,  # 10MB
    ) -> dict:
        """上传请假材料"""
        # 确保目录存在
        cls.ensure_directories()

        # 验证文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置文件指针

        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"文件大小超过限制 ({max_size / 1024 / 1024}MB)"
            )

        # 验证文件类型
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=415,
                detail=f"不支持的文件类型。允许的类型: {', '.join(allowed_extensions)}"
            )

        # 生成文件名并保存
        filename = cls.generate_filename(file.filename, leave_id)
        file_path = cls.MATERIALS_DIR / filename

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return {
                "filename": filename,
                "original_name": file.filename,
                "file_path": str(file_path),
                "file_size": file_size,
                "uploaded_at": datetime.now().isoformat(),
                "url": f"/uploads/materials/{filename}"
            }
        except Exception as e:
            # 如果保存失败，删除可能已创建的文件
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    @classmethod
    def delete_material(cls, filename: str) -> bool:
        """删除材料文件"""
        file_path = cls.MATERIALS_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    @classmethod
    def get_material_path(cls, filename: str) -> Optional[Path]:
        """获取材料文件路径"""
        file_path = cls.MATERIALS_DIR / filename
        if file_path.exists():
            return file_path
        return None
