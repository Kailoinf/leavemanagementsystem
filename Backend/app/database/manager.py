from sqlmodel import SQLModel
from app.database.connection import engine


class DatabaseManager:
    def __init__(self):
        SQLModel.metadata.create_all(engine, checkfirst=True)

    def get_session(self):
        from app.database.connection import get_session
        return get_session()


db_manager = DatabaseManager()