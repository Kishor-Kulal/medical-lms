from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Course, CourseEnrollment, Module, User
from app.auth import get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])


# Response Models
class CourseBasic(BaseModel):
    id: str
    title: str
    code: Optional[str]
    faculty_name: Optional[str]
    
    class Config:
        from_attributes = True


class CourseDetail(BaseModel):
    id: str
    title: str
    code: Optional[str]
    description: Optional[str]
    faculty_name: Optional[str]
    
    class Config:
        from_attributes = True


class ModuleResponse(BaseModel):
    id: str
    title: str
    sequence_order: int
    
    class Config:
        from_attributes = True


# 1. GET /courses/my-courses - List all courses student is enrolled in
@router.get("/my-courses", response_model=List[CourseBasic])
def get_my_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all courses the logged-in student is enrolled in
    """
    # Get all course enrollments for this student
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.student_id == current_user.id,
        CourseEnrollment.tenant_id == current_user.tenant_id
    ).all()
    
    # Get course details for each enrollment
    courses = []
    for enrollment in enrollments:
        course = db.query(Course).filter(
            Course.id == enrollment.course_id,
            Course.is_active == True
        ).first()
        
        if course:
            courses.append(CourseBasic(
                id=str(course.id),
                title=course.title,
                code=course.code,
                faculty_name=course.faculty_name
            ))
    
    return courses


# 2. GET /courses/{id} - Get detailed info for one course
@router.get("/{course_id}", response_model=CourseDetail)
def get_course_detail(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information (Syllabus, Faculty name) for one course
    """
    # Check if student is enrolled in this course
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id,
        CourseEnrollment.tenant_id == current_user.tenant_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )
    
    # Get course details
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.is_active == True
    ).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return CourseDetail(
        id=str(course.id),
        title=course.title,
        code=course.code,
        description=course.description,
        faculty_name=course.faculty_name
    )


# 3. GET /courses/{id}/modules - Get list of chapters/modules for a course
@router.get("/{course_id}/modules", response_model=List[ModuleResponse])
def get_course_modules(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the list of chapters/modules for a course
    """
    # Check if student is enrolled
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == current_user.id,
        CourseEnrollment.tenant_id == current_user.tenant_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )
    
    # Get modules ordered by sequence
    modules = db.query(Module).filter(
        Module.course_id == course_id,
        Module.tenant_id == current_user.tenant_id
    ).order_by(Module.sequence_order).all()
    
    return [
        ModuleResponse(
            id=str(module.id),
            title=module.title,
            sequence_order=module.sequence_order
        )
        for module in modules
    ]