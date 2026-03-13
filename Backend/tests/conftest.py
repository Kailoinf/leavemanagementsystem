"""Pytest 配置和共享 fixtures"""
import pytest
from sqlmodel import SQLModel, create_engine, Session, text
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile

# 重要：在导入 app 之前先导入所有 models，确保 SQLModel.metadata 包含所有表定义
from app.models import (
    Admin, Reviewer, Student, Teacher, Course,
    Leave, LeaveStatus, LeaveType, Login, StudentCourse, School, Role
)

# 导入 app
from app.main import app
from app.database.connection import get_session


@pytest.fixture(scope="function")
def temp_db_file():
    """创建临时数据库文件"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = Path(f.name)
    yield temp_path
    # 清理
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture(scope="function")
def test_engine(temp_db_file):
    """创建测试数据库引擎（使用临时文件）"""
    # 使用临时文件作为数据库，禁用同线程检查以支持 TestClient 的多线程测试
    db_url = f"sqlite:///{temp_db_file}"
    engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )

    # 创建所有表
    SQLModel.metadata.create_all(engine)

    # 验证表是否被创建
    with Session(engine) as session:
        result = session.exec(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.all()
        print(f"\n=== DEBUG: Tables created in test_engine ({temp_db_file}): {[t[0] for t in tables]} ===")

    yield engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """创建测试数据库会话"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_engine):
    """创建测试客户端"""

    # 覆盖依赖
    def get_test_session():
        session = Session(test_engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
