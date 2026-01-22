"""
Create demo users matching data.sql structure
Command: python create_demo_user.py
"""

from app.database import SessionLocal
from app.models import Tenant, User, UserRole
from app.auth import hash_password
import uuid

db = SessionLocal()

print("Creating demo data...\n")

# Fixed UUIDs (same as data.sql)
TENANT_ID = uuid.UUID('11111111-1111-1111-1111-111111111111')
ADMIN_ID = uuid.UUID('22222222-2222-2222-2222-222222222222')
FACULTY_ID = uuid.UUID('33333333-3333-3333-3333-333333333333')
STUDENT_ID = uuid.UUID('44444444-4444-4444-4444-444444444444')

# 1. Create Tenant (Apollo Medical College)
tenant = Tenant(
    id=TENANT_ID,
    name="Apollo Medical College",
    domain="apollo.medlms.com",
    is_active=True
)
db.add(tenant)
db.commit()
print(f"✅ Tenant created: {tenant.name}")

# 2. Create Admin User
admin = User(
    id=ADMIN_ID,
    tenant_id=TENANT_ID,
    email="admin@apollo.edu",
    password_hash=hash_password("password"),
    full_name="Dean of Medicine",
    role=UserRole.ADMIN,
    is_active=True
)
db.add(admin)
db.commit()
print(f"✅ Admin created: {admin.email}")

# 3. Create Faculty (Dr. House)
faculty = User(
    id=FACULTY_ID,
    tenant_id=TENANT_ID,
    email="house@apollo.edu",
    password_hash=hash_password("password"),
    full_name="Dr. Gregory House",
    role=UserRole.FACULTY,
    is_active=True
)
db.add(faculty)
db.commit()
print(f"✅ Faculty created: {faculty.email}")

# 4. Create Student (Rahul Sharma)
student = User(
    id=STUDENT_ID,
    tenant_id=TENANT_ID,
    email="rahul@apollo.edu",
    password_hash=hash_password("password"),
    full_name="Rahul Sharma",
    role=UserRole.STUDENT,
    is_active=True
)
db.add(student)
db.commit()
print(f"✅ Student created: {student.email}")

print("\n🎉 Demo users created successfully!")
print("\n🔑 You can login with any of these:")
print("\nAdmin:")
print("  Email: admin@apollo.edu")
print("  Password: password")
print("\nFaculty:")
print("  Email: house@apollo.edu")
print("  Password: password")
print("\nStudent:")
print("  Email: rahul@apollo.edu")
print("  Password: password")

db.close()