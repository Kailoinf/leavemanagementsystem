from fastapi import APIRouter
from app.api.v1 import auth, students, teachers, reviewers, courses, leaves, status, student_courses

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(students.router, tags=["students"])
api_router.include_router(teachers.router, tags=["teachers"])
api_router.include_router(reviewers.router, tags=["reviewers"])
api_router.include_router(courses.router, tags=["courses"])
api_router.include_router(leaves.router, tags=["leaves"])
api_router.include_router(status.router, tags=["status"])
api_router.include_router(student_courses.router, tags=["student-courses"])
