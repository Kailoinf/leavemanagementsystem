from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
