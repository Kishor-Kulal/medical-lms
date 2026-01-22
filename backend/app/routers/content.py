from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import ContentItem, Module, CourseEnrollment, LessonProgress, User
from app.auth import get_current_user

router = APIRouter(prefix="/content", tags=["Content"])


# Response Models
class LessonBasic(BaseModel):
    id: str
    title: str
    content_type: str
    duration_minutes: Optional[int]
    sequence_order: int
    is_completed: bool = False
    
    class Config:
        from_attributes = True


class LessonDetail(BaseModel):
    id: str
    title: str
    content_type: str
    file_url: Optional[str]
    text_content: Optional[str]
    duration_minutes: Optional[int]
    sequence_order: int
    is_completed: bool = False
    
    class Config:
        from_attributes = True


class CompleteResponse(BaseModel):
    message: str
    lesson_id: str
    completed_at: datetime


# 1. GET /content/{module_id}/lessons - List all lessons in a module
@router.get("/{module_id}/lessons", response_model=List[LessonBasic])
def get_module_lessons(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all lessons in a specific module
    """
    # Get module to find course_id
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.tenant_id == current_user.tenant_id
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if student is enrolled in the course
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == module.course_id,
        CourseEnrollment.student_id == current_user.id,
        CourseEnrollment.tenant_id == current_user.tenant_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )
    
    # Get all lessons in this module
    lessons = db.query(ContentItem).filter(
        ContentItem.module_id == module_id,
        ContentItem.tenant_id == current_user.tenant_id
    ).order_by(ContentItem.sequence_order).all()
    
    # Check completion status for each lesson
    result = []
    for lesson in lessons:
        # Check if student completed this lesson
        progress = db.query(LessonProgress).filter(
            LessonProgress.student_id == current_user.id,
            LessonProgress.content_item_id == lesson.id
        ).first()
        
        result.append(LessonBasic(
            id=str(lesson.id),
            title=lesson.title,
            content_type=lesson.type.value,
            duration_minutes=lesson.duration_minutes,
            sequence_order=lesson.sequence_order,
            is_completed=progress.is_completed if progress else False
        ))
    
    return result


# 2. GET /content/lesson/{id} - Get actual content of a lesson
@router.get("/lesson/{lesson_id}", response_model=LessonDetail)
def get_lesson_content(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the actual content (Video URL, PDF link, Text) of a lesson
    """
    # Get lesson
    lesson = db.query(ContentItem).filter(
        ContentItem.id == lesson_id,
        ContentItem.tenant_id == current_user.tenant_id
    ).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to find course
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    
    # Check enrollment
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == module.course_id,
        CourseEnrollment.student_id == current_user.id,
        CourseEnrollment.tenant_id == current_user.tenant_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )
    
    # Check completion status
    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == current_user.id,
        LessonProgress.content_item_id == lesson.id
    ).first()
    
    return LessonDetail(
        id=str(lesson.id),
        title=lesson.title,
        content_type=lesson.type.value,
        file_url=lesson.file_url,
        text_content=lesson.text_content,
        duration_minutes=lesson.duration_minutes,
        sequence_order=lesson.sequence_order,
        is_completed=progress.is_completed if progress else False
    )


# 3. POST /content/lesson/{id}/complete - Mark lesson as done
@router.post("/lesson/{lesson_id}/complete", response_model=CompleteResponse)
def mark_lesson_complete(
    lesson_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a lesson as "Done" (for progress tracking)
    """
    # Get lesson
    lesson = db.query(ContentItem).filter(
        ContentItem.id == lesson_id,
        ContentItem.tenant_id == current_user.tenant_id
    ).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    # Get module to find course
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    
    # Check enrollment
    enrollment = db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == module.course_id,
        CourseEnrollment.student_id == current_user.id,
        CourseEnrollment.tenant_id == current_user.tenant_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )
    
    # Check if progress already exists
    progress = db.query(LessonProgress).filter(
        LessonProgress.student_id == current_user.id,
        LessonProgress.content_item_id == lesson.id
    ).first()
    
    completed_time = datetime.utcnow()
    
    if progress:
        # Update existing progress
        progress.is_completed = True
        progress.completed_at = completed_time
    else:
        # Create new progress record
        from app.models import LessonProgress as LessonProgressModel
        import uuid
        progress = LessonProgressModel(
            id=uuid.uuid4(),
            student_id=current_user.id,
            content_item_id=lesson.id,
            is_completed=True,
            completed_at=completed_time
        )
        db.add(progress)
    
    db.commit()
    
    return CompleteResponse(
        message="Lesson marked as complete",
        lesson_id=str(lesson.id),
        completed_at=completed_time
    )