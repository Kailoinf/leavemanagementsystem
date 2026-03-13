from sqlmodel import create_engine, Session
from app.config.settings import settings

# 创建数据库引擎
engine = create_engine(settings.database_url, echo=False)


def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session