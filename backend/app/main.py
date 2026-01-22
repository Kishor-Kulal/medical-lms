from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import auth, users, courses, content
from app.database import create_tables
from app.models import (
    Tenant, User, Department, Batch, StudentDetail, 
    Course, CourseEnrollment, Module, ContentItem, LessonProgress
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when server starts and stops
    """
    # Startup: Create database tables
    print("🚀 Starting server...")
    create_tables()
    yield
    # Shutdown: cleanup if needed
    print("🛑 Shutting down server...")


# Create FastAPI app
app = FastAPI(
    title="Medical LMS API",
    description="Backend API for Medical Learning Management System",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(courses.router, prefix="/api/v1")  # Sprint 2
app.include_router(content.router, prefix="/api/v1")  # Sprint 2


# Home page
@app.get("/")
def home():
    return {
        "message": "Medical LMS API is running",
        "docs": "Go to /docs for API documentation"
    }


# Health check
@app.get("/health")
def health():
    return {"status": "healthy"}