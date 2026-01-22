from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models import User, UserRole
from app.auth import verify_password, create_token, get_current_user, hash_password
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Request/Response models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "STUDENT"  # Default role
    # tenant_id: Optional[str] = None  # Optional for now


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    tenant_id: str


# 1. POST /auth/signup - Register new user
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(signup_data: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    valid_roles = ["ADMIN", "FACULTY", "STUDENT"]
    if signup_data.role.upper() not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Get or create tenant_id (for now using a default tenant)
    # TODO: In production, get tenant from subdomain or request
    if signup_data.tenant_id:
        tenant_id = uuid.UUID(signup_data.tenant_id)
    else:
        # Use first tenant or create a default one
        from app.models import Tenant
        default_tenant = db.query(Tenant).first()
        if not default_tenant:
            # Create a default tenant if none exists
            default_tenant = Tenant(
                id=uuid.uuid4(),
                name="Default Medical College",
                domain="default.medlms.com",
                is_active=True
            )
            db.add(default_tenant)
            db.commit()
        tenant_id = default_tenant.id
    
    # Create new user
    new_user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=signup_data.email,
        password_hash=hash_password(signup_data.password),
        full_name=signup_data.full_name,
        phone=signup_data.phone,
        role=UserRole[signup_data.role.upper()],
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role.value,
        tenant_id=str(new_user.tenant_id)
    )


# 2. POST /auth/login - Login with email and password
@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user and return JWT token
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )
    
    # Check password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password is incorrect"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is disabled"
        )
    
    # Create token
    token = create_token(str(user.id))
    
    return TokenResponse(access_token=token)


# 3. POST /auth/refresh - Refresh token (Simple version - just create new token)
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Create a new token for logged-in user
    """
    new_token = create_token(str(current_user.id))
    return TokenResponse(access_token=new_token)


# 4. POST /auth/reset-password - Send password reset email
@router.post("/reset-password")
def reset_password(email: EmailStr, db: Session = Depends(get_db)):
    """
    Request password reset (Email sending not implemented yet)
    """
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    
    # Don't reveal if email exists or not (security)
    return {
        "message": "If this email exists, you will receive password reset instructions"
    }


# 5. GET /auth/me - Get current user info
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user details
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        tenant_id=str(current_user.tenant_id)
    )