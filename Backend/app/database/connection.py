from sqlmodel import create_engine, Session
from app.config.settings import settings

# 创建数据库引擎
# 对于 SQLite，需要禁用同线程检查以支持 TestClient 的多线程测试
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session