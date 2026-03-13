from fastapi import APIRouter
from app.api.v1 import auth, students, teachers, reviewers, courses, leaves, status, student_courses, files, export, import_data

api_router = APIRouter()

# Include all routers with prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
api_router.include_router(reviewers.router, prefix="/reviewers", tags=["reviewers"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(leaves.router, prefix="/leaves", tags=["leaves"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(student_courses.router, prefix="/student-courses", tags=["student-courses"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(import_data.router, prefix="/import", tags=["import"])
