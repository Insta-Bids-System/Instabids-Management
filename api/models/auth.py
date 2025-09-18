from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime
import re

class UserType(str):
    PROPERTY_MANAGER = "property_manager"
    CONTRACTOR = "contractor"
    TENANT = "tenant"
    ADMIN = "admin"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    user_type: Literal["property_manager", "contractor", "tenant"]
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, pattern=r"^\+?1?\d{9,15}$")
    organization_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('organization_name')
    def validate_organization(cls, v, values):
        if values.get('user_type') == 'property_manager' and not v:
            raise ValueError('Organization name required for property managers')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class VerifyEmailRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class NewPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"\d", v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    user_type: str
    organization_id: Optional[str]
    email_verified: bool
    phone_verified: bool
    created_at: datetime

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse

class RegisterResponse(BaseModel):
    user_id: str
    email: str
    requires_verification: bool = True
    message: str = "Registration successful. Please verify your email."

class MessageResponse(BaseModel):
    success: bool
    message: str

class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    type: Literal["property_management", "contractor", "other"]
    
class UserProfileCreate(BaseModel):
    email: EmailStr
    phone: Optional[str]
    full_name: str
    user_type: str
    organization_id: Optional[str]
    profile_data: Optional[dict] = {}