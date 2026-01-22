from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Enum, Date, Time
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"


class ContentType(str, enum.Enum):
    PDF = "PDF"
    VIDEO = "VIDEO"
    TEXT = "TEXT"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"


class QuestionType(str, enum.Enum):
    MCQ = "MCQ"
    DESCRIPTIVE = "DESCRIPTIVE"


class ExamStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"


# ============================================================================
# MODULE 1: CORE (Tenancy & Users)
# ============================================================================

class Tenant(Base):
    """Medical Colleges (e.g., AIIMS Delhi, Apollo Medical College)"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class User(Base):
    """Stores everyone: Admins, Faculty, Students"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)  # Unique per tenant
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    bio = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============================================================================
# MODULE 2: ACADEMIC STRUCTURE
# ============================================================================

class Department(Base):
    """E.g., Anatomy, Physiology, Pathology"""
    __tablename__ = "departments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    head_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # HOD (Optional)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class Batch(Base):
    """E.g., MBBS Batch of 2024"""
    __tablename__ = "batches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)  # "Class of 2024"
    start_year = Column(Integer, nullable=False)  # 2024
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class StudentDetail(Base):
    """Extra info specific to students, linked to users table"""
    __tablename__ = "student_details"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"))
    enrollment_no = Column(String, unique=True)  # University Roll No
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============================================================================
# MODULE 3: COURSE MANAGEMENT
# ============================================================================

class Course(Base):
    """E.g., Human Anatomy - Semester 1"""
    __tablename__ = "courses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    title = Column(String, nullable=False)
    code = Column(String)  # e.g., "ANAT101"
    description = Column(Text)  # Added for syllabus
    faculty_name = Column(String)  # Simplified for Phase 1
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class CourseEnrollment(Base):
    """Which student is in which course"""
    __tablename__ = "course_enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============================================================================
# MODULE 4: CONTENT (LMS)
# ============================================================================

class Module(Base):
    """Chapters inside a course"""
    __tablename__ = "modules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    sequence_order = Column(Integer, nullable=False)  # 1, 2, 3...
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class ContentItem(Base):
    """The actual files or lessons"""
    __tablename__ = "content_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    title = Column(String, nullable=False)
    type = Column(Enum(ContentType), nullable=False)  # PDF/VIDEO/TEXT (as per doc)
    file_url = Column(String)  # S3 Link
    text_content = Column(Text)  # For TEXT type
    duration_minutes = Column(Integer)  # For videos
    sequence_order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class LessonProgress(Base):
    """Track which lessons student completed (Not in doc but needed for Sprint 2)"""
    __tablename__ = "lesson_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("content_items.id"), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============================================================================
# MODULE 5: ATTENDANCE
# ============================================================================

class ClassSession(Base):
    """A specific lecture that took place"""
    __tablename__ = "class_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic = Column(String)  # What was taught
    session_date = Column(Date, nullable=False)
    start_time = Column(Time)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class AttendanceRecord(Base):
    """Individual student status for a session"""
    __tablename__ = "attendance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("class_sessions.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)  # PRESENT, ABSENT, LATE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# ============================================================================
# MODULE 6: EXAMS & GRADING (Simplified for Phase 1)
# ============================================================================

class Exam(Base):
    """The exam event"""
    __tablename__ = "exams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    total_marks = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class Question(Base):
    """The Question Bank"""
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    type = Column(Enum(QuestionType), nullable=False)  # MCQ/DESCRIPTIVE
    marks = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class ExamQuestion(Base):
    """Linking Questions to an Exam"""
    __tablename__ = "exam_questions"
    
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), primary_key=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StudentAttempt(Base):
    """When a student takes an exam"""
    __tablename__ = "student_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score_obtained = Column(Integer)  # Calculated later
    status = Column(Enum(ExamStatus), nullable=False)  # SUBMITTED/PENDING
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)