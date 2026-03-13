from fastapi import APIRouter, Depends
from datetime import datetime
from sqlmodel import Session
from app.database.connection import get_session
from app.services.auth import AuthService

router = APIRouter()


@router.get("/", summary="健康检查")
async def root(session: Session = Depends(get_session)):
    """健康检查端点"""
    if AuthService.get_admins_count(session) == 0:
        return {"status": "unhealthy", "message": "No admin found"}
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
