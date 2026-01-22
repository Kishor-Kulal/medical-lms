"""
Create demo data for Sprint 2 (Courses and Content)
Matches data.sql structure
Command: python create_sprint2_demo_data.py
"""

from app.database import SessionLocal
from app.models import (
    Tenant, User, Department, Batch, StudentDetail,
    Course, CourseEnrollment, Module, ContentItem, ContentType
)
import uuid
from datetime import datetime

db = SessionLocal()

print("Creating Sprint 2 demo data...\n")

# Fixed UUIDs (matching data.sql)
TENANT_ID = uuid.UUID('11111111-1111-1111-1111-111111111111')
FACULTY_ID = uuid.UUID('33333333-3333-3333-3333-333333333333')
STUDENT_ID = uuid.UUID('44444444-4444-4444-4444-444444444444')
DEPT_ID = uuid.UUID('55555555-5555-5555-5555-555555555555')
BATCH_ID = uuid.UUID('66666666-6666-6666-6666-666666666666')
COURSE_ID = uuid.UUID('77777777-7777-7777-7777-777777777777')
MODULE_ID = uuid.UUID('88888888-8888-8888-8888-888888888888')

# Get existing tenant and users
tenant = db.query(Tenant).filter(Tenant.id == TENANT_ID).first()
student = db.query(User).filter(User.id == STUDENT_ID).first()
faculty = db.query(User).filter(User.id == FACULTY_ID).first()

if not tenant or not student or not faculty:
    print("❌ Error: Run create_demo_user.py first!")
    db.close()
    exit()

# 1. Create Department (Anatomy)
dept = Department(
    id=DEPT_ID,
    tenant_id=TENANT_ID,
    name="Anatomy",
    head_user_id=FACULTY_ID  # Dr. House is HOD
)
db.add(dept)
db.commit()
print(f"✅ Department created: {dept.name}")

# 2. Create Batch (MBBS 2025)
batch = Batch(
    id=BATCH_ID,
    tenant_id=TENANT_ID,
    name="MBBS Batch 2025",
    start_year=2025
)
db.add(batch)
db.commit()
print(f"✅ Batch created: {batch.name}")

# 3. Link Student to Batch
student_detail = StudentDetail(
    user_id=STUDENT_ID,
    batch_id=BATCH_ID,
    enrollment_no="MBBS-25-001"
)
db.add(student_detail)
db.commit()
print(f"✅ Student linked to batch: {student.full_name}")

# 4. Create Course (Human Anatomy - Sem 1)
course = Course(
    id=COURSE_ID,
    tenant_id=TENANT_ID,
    dept_id=DEPT_ID,
    title="Human Anatomy - Sem 1",
    code="ANAT101",
    description="Introduction to human anatomy covering skeletal system and muscles",
    faculty_name="Dr. Gregory House",
    is_active=True
)
db.add(course)
db.commit()
print(f"✅ Course created: {course.title}")

# 5. Enroll Student in Course
enrollment = CourseEnrollment(
    id=uuid.uuid4(),
    course_id=COURSE_ID,
    student_id=STUDENT_ID,
    tenant_id=TENANT_ID
)
db.add(enrollment)
db.commit()
print(f"✅ Student enrolled in course")

# 6. Create Modules for the Course
module1 = Module(
    id=MODULE_ID,
    tenant_id=TENANT_ID,
    course_id=COURSE_ID,
    title="Module 1: Upper Limb",
    sequence_order=1
)

module2_id = uuid.uuid4()
module2 = Module(
    id=module2_id,
    tenant_id=TENANT_ID,
    course_id=COURSE_ID,
    title="Module 2: Lower Limb",
    sequence_order=2
)

module3_id = uuid.uuid4()
module3 = Module(
    id=module3_id,
    tenant_id=TENANT_ID,
    course_id=COURSE_ID,
    title="Module 3: Head and Neck",
    sequence_order=3
)

db.add_all([module1, module2, module3])
db.commit()
print(f"✅ Modules created: 3 modules")

# 7. Create Content Items (Lessons) for Module 1: Upper Limb
print("\nCreating lessons for Module 1: Upper Limb...")

lessons_module1 = [
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Introduction to Upper Limb Anatomy",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        duration_minutes=15,
        sequence_order=1
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Bones of the Upper Limb - Lecture Notes",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/upper-limb-bones.pdf",
        sequence_order=2
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Humerus Bone - Detailed Study",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=humerus_anatomy",
        duration_minutes=25,
        sequence_order=3
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Key Points: Humerus Anatomy",
        type=ContentType.TEXT,
        text_content="""
# Humerus - The Arm Bone

## Overview
The humerus is the longest and largest bone of the upper limb. It connects the shoulder to the elbow.

## Key Features

### Proximal End (Head)
- **Head**: Articulates with glenoid cavity of scapula
- **Anatomical Neck**: Narrow groove below the head
- **Greater Tubercle**: Lateral projection
- **Lesser Tubercle**: Anterior projection
- **Surgical Neck**: Most commonly fractured part

### Shaft (Body)
- Deltoid tuberosity: Attachment for deltoid muscle
- Radial groove: For radial nerve passage
- Triangular in upper part, cylindrical in lower part

### Distal End
- **Capitulum**: Articulates with radius
- **Trochlea**: Articulates with ulna
- **Medial Epicondyle**: Larger, for flexor muscles
- **Lateral Epicondyle**: Smaller, for extensor muscles
- **Coronoid Fossa**: Anterior, for coronoid process
- **Olecranon Fossa**: Posterior, for olecranon process

## Clinical Significance
- Common fracture site: Surgical neck
- Radial nerve injury: Can occur with mid-shaft fractures
- Supracondylar fractures: Common in children
        """,
        sequence_order=4
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Radius and Ulna - Forearm Bones",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=radius_ulna_video",
        duration_minutes=20,
        sequence_order=5
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Forearm Bones Study Guide",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/forearm-bones.pdf",
        sequence_order=6
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Muscles of Upper Limb - Overview",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=upper_limb_muscles",
        duration_minutes=30,
        sequence_order=7
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Quick Reference: Major Muscles",
        type=ContentType.TEXT,
        text_content="""
# Major Muscles of Upper Limb

## Shoulder Muscles
1. **Deltoid**: Abducts arm
2. **Rotator Cuff Muscles**:
   - Supraspinatus: Abduction (first 15°)
   - Infraspinatus: Lateral rotation
   - Teres minor: Lateral rotation
   - Subscapularis: Medial rotation

## Arm Muscles
### Anterior Compartment (Flexors)
1. **Biceps Brachii**: Flexes elbow, supinates forearm
2. **Brachialis**: Main flexor of elbow
3. **Coracobrachialis**: Flexes and adducts arm

### Posterior Compartment (Extensors)
1. **Triceps Brachii**: Extends elbow
   - Long head
   - Lateral head
   - Medial head

## Forearm Muscles
### Anterior (Flexors)
- Superficial: Pronator teres, FCR, Palmaris longus, FCU
- Intermediate: FDS
- Deep: FDP, FPL, Pronator quadratus

### Posterior (Extensors)
- Superficial: Brachioradialis, ECRL, ECRB, EDC, ECU
- Deep: Supinator, EPL, EPB, APL
        """,
        sequence_order=8
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Blood Supply of Upper Limb",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/upper-limb-blood-supply.pdf",
        sequence_order=9
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=MODULE_ID,
        title="Nerves of Upper Limb - Brachial Plexus",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=brachial_plexus",
        duration_minutes=35,
        sequence_order=10
    )
]

db.add_all(lessons_module1)
db.commit()
print(f"✅ Module 1 lessons created: {len(lessons_module1)} lessons")

# 8. Create Content Items for Module 2: Lower Limb
print("\nCreating lessons for Module 2: Lower Limb...")

lessons_module2 = [
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module2_id,
        title="Introduction to Lower Limb",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=lower_limb_intro",
        duration_minutes=18,
        sequence_order=1
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module2_id,
        title="Femur - The Thigh Bone",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=femur_anatomy",
        duration_minutes=22,
        sequence_order=2
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module2_id,
        title="Femur Anatomy Summary",
        type=ContentType.TEXT,
        text_content="""
# Femur - The Thigh Bone

## Overview
- Longest and strongest bone in the body
- Bears the weight of entire body
- Connects hip to knee

## Proximal End
- **Head**: Ball-shaped, articulates with acetabulum
- **Neck**: Connects head to shaft (common fracture site in elderly)
- **Greater Trochanter**: Lateral prominence
- **Lesser Trochanter**: Medial and posterior
- **Intertrochanteric Line**: Anterior, between trochanters
- **Intertrochanteric Crest**: Posterior, between trochanters

## Shaft
- Strong and cylindrical
- **Linea Aspera**: Prominent posterior ridge

## Distal End
- **Medial Condyle**: Larger
- **Lateral Condyle**: Smaller
- **Intercondylar Fossa**: Between condyles
- Articulates with tibia and patella

## Clinical Points
- Neck of femur fractures common in osteoporosis
- Strong bone, requires high impact to fracture in young adults
        """,
        sequence_order=3
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module2_id,
        title="Tibia and Fibula - Leg Bones",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/tibia-fibula.pdf",
        sequence_order=4
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module2_id,
        title="Muscles of Lower Limb",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=lower_limb_muscles",
        duration_minutes=40,
        sequence_order=5
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module2_id,
        title="Hip Joint Anatomy",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/hip-joint.pdf",
        sequence_order=6
    )
]

db.add_all(lessons_module2)
db.commit()
print(f"✅ Module 2 lessons created: {len(lessons_module2)} lessons")

# 9. Create Content Items for Module 3: Head and Neck
print("\nCreating lessons for Module 3: Head and Neck...")

lessons_module3 = [
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module3_id,
        title="Skull Bones - Overview",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=skull_bones",
        duration_minutes=25,
        sequence_order=1
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module3_id,
        title="Cranial Cavity and Brain",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/cranial-cavity.pdf",
        sequence_order=2
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module3_id,
        title="Facial Bones Summary",
        type=ContentType.TEXT,
        text_content="""
# Facial Bones

## Paired Bones (6 pairs = 12 bones)
1. **Maxilla** (2): Upper jaw, forms part of orbit and nasal cavity
2. **Palatine** (2): Forms posterior hard palate
3. **Zygomatic** (2): Cheek bones
4. **Nasal** (2): Bridge of nose
5. **Lacrimal** (2): Smallest facial bones, medial wall of orbit
6. **Inferior Nasal Conchae** (2): Inside nasal cavity

## Unpaired Bones (2 bones)
1. **Vomer**: Forms inferior nasal septum
2. **Mandible**: Lower jaw, only movable skull bone

## Key Points
- Total facial bones: 14
- Maxilla and mandible contain teeth
- Mandible articulates with temporal bone at TMJ
- Zygomatic arch formed by zygomatic and temporal bones
        """,
        sequence_order=3
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module3_id,
        title="Neck Muscles and Triangles",
        type=ContentType.VIDEO,
        file_url="https://www.youtube.com/watch?v=neck_anatomy",
        duration_minutes=30,
        sequence_order=4
    ),
    ContentItem(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        module_id=module3_id,
        title="Cranial Nerves - Complete Guide",
        type=ContentType.PDF,
        file_url="https://s3.amazonaws.com/medical-lms/anatomy/cranial-nerves.pdf",
        sequence_order=5
    )
]

db.add_all(lessons_module3)
db.commit()
print(f"✅ Module 3 lessons created: {len(lessons_module3)} lessons")

print("\n🎉 Sprint 2 demo data created successfully!")

# Calculate totals
total_modules = 3
total_lessons = len(lessons_module1) + len(lessons_module2) + len(lessons_module3)

print(f"\n📊 Data Summary:")
print(f"   - Departments: 1 (Anatomy)")
print(f"   - Batches: 1 (MBBS 2025)")
print(f"   - Courses: 1 (Human Anatomy)")
print(f"   - Modules: {total_modules}")
print(f"   - Total Lessons: {total_lessons}")
print(f"     • Module 1: {len(lessons_module1)} lessons")
print(f"     • Module 2: {len(lessons_module2)} lessons")
print(f"     • Module 3: {len(lessons_module3)} lessons")

print("\n📚 Lesson Breakdown by Type:")
video_count = sum(1 for m in [lessons_module1, lessons_module2, lessons_module3] for l in m if l.type == ContentType.VIDEO)
pdf_count = sum(1 for m in [lessons_module1, lessons_module2, lessons_module3] for l in m if l.type == ContentType.PDF)
text_count = sum(1 for m in [lessons_module1, lessons_module2, lessons_module3] for l in m if l.type == ContentType.TEXT)

print(f"   🎥 Videos: {video_count}")
print(f"   📄 PDFs: {pdf_count}")
print(f"   📝 Text: {text_count}")

print("\n🧪 Test these endpoints:")
print("1. GET /api/v1/courses/my-courses")
print("2. GET /api/v1/courses/{course_id}")
print("3. GET /api/v1/courses/{course_id}/modules")
print("4. GET /api/v1/content/{module_id}/lessons")
print("5. GET /api/v1/content/lesson/{lesson_id}")
print("6. POST /api/v1/content/lesson/{lesson_id}/complete")

print("\n🔑 Login credentials:")
print("   Email: rahul@apollo.edu")
print("   Password: password")

print(f"\n📋 Important IDs for testing:")
print(f"   Tenant ID:  {TENANT_ID}")
print(f"   Student ID: {STUDENT_ID}")
print(f"   Course ID:  {COURSE_ID}")
print(f"   Module 1 ID: {MODULE_ID}")
print(f"   Module 2 ID: {module2_id}")
print(f"   Module 3 ID: {module3_id}")

print("\n💡 Tip: Copy any lesson ID from the API response to test lesson completion!")

db.close()