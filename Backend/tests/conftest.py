"""Pytest 配置和共享 fixtures"""
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile

from app.main import app


@pytest.fixture(scope="function")
def test_db():
    """创建测试数据库（内存数据库）"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_db):
    """创建测试客户端"""
    # 覆盖数据库依赖（get_session 是生成器，需要特殊处理）
    from app.database.connection import get_session

    def get_test_session():
        yield test_db

    app.dependency_overrides[get_session] = get_test_session

    with TestClient(app) as test_client:
        yield test_client

    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def temp_db_file():
    """创建临时数据库文件"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = Path(f.name)
    yield temp_path
    # 清理
    if temp_path.exists():
        temp_path.unlink()
