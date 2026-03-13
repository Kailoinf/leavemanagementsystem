from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.database.connection import engine
from app.api.v1.router import api_router


# Lifespan事件处理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    SQLModel.metadata.create_all(engine, checkfirst=True)
    yield
    # 关闭时的清理工作（如果需要）


# 创建FastAPI应用
app = FastAPI(title="Leave Management System", lifespan=lifespan)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix="/api/v1")

# 挂载静态文件目录
import os
from pathlib import Path
from app.services.file import FileService

# 确保上传目录存在
FileService.ensure_directories()

# 挂载静态文件服务
if os.path.exists(FileService.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=str(FileService.UPLOAD_DIR)), name="uploads")
