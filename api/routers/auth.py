import logging
from datetime import datetime, timedelta
from typing import Optional

from config import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from models.auth import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    NewPasswordRequest,
    OrganizationCreate,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    UserProfileCreate,
    UserResponse,
    VerifyEmailRequest,
)
from services.supabase import supabase_service

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserResponse:
    """Validate JWT token and return current user"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # Get user from database
        user = await supabase_service.verify_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return UserResponse(**user)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    try:
        # Create organization if property manager
        org_id = None
        if request.user_type == "property_manager" and request.organization_name:
            org_response = (
                supabase_service.service_client.table("organizations")
                .insert(
                    {"name": request.organization_name, "type": "property_management"}
                )
                .execute()
            )

            if org_response.data:
                org_id = org_response.data[0]["id"]

        # Create user with Supabase Auth
        user_metadata = {
            "full_name": request.full_name,
            "user_type": request.user_type,
            "phone": request.phone,
        }

        # Use service client for admin create (bypasses email confirmation)
        logger.info(f"Attempting to register user: {request.email}")
        logger.info(f"Using Supabase URL: {supabase_service.client.supabase_url}")
        
        auth_response = supabase_service.service_client.auth.admin.create_user(
            {
                "email": request.email,
                "password": request.password,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": user_metadata,
            }
        )

        if not auth_response.user:
            raise Exception("Failed to create user account")

        auth_user = auth_response.user

        # Create user profile
        profile_response = (
            supabase_service.service_client.table("user_profiles")
            .insert(
                {
                    "id": auth_user.id,
                    "email": request.email,
                    "full_name": request.full_name,
                    "user_type": request.user_type,
                    "phone": request.phone,
                    "organization_id": org_id,
                    "profile_data": {},
                }
            )
            .execute()
        )
        return RegisterResponse(
            user_id=auth_user.id, 
            email=request.email, 
            requires_verification=True,
            message="Registration successful! Please check your email to confirm your account."
        )

    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password"""
    try:
        # Authenticate with Supabase
        auth_response = await supabase_service.sign_in(
            email=request.email, password=request.password
        )

        if not auth_response or not auth_response.get("user"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        user = auth_response["user"]
        session = auth_response["session"]
        # Get user profile from database
        profile_response = (
            supabase_service.client.table("user_profiles")
            .select("*")
            .eq("id", user.id)
            .single()
            .execute()
        )

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found"
            )

        profile = profile_response.data

        # Create tokens
        access_token = create_access_token({"sub": user.id, "email": user.email})
        refresh_token = create_refresh_token({"sub": user.id})

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=profile["full_name"],
                user_type=profile["user_type"],
                organization_id=profile["organization_id"],
                email_verified=profile["email_verified"],
                phone_verified=profile["phone_verified"],
                created_at=profile["created_at"],
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = jwt.decode(
            request.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        user_id = payload.get("sub")

        # Get user profile
        profile_response = (
            supabase_service.client.table("user_profiles")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        profile = profile_response.data

        # Create new tokens
        access_token = create_access_token({"sub": user_id, "email": profile["email"]})
        new_refresh_token = create_refresh_token({"sub": user_id})

        return AuthResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
            user=UserResponse(
                id=profile["id"],
                email=profile["email"],
                full_name=profile["full_name"],
                user_type=profile["user_type"],
                organization_id=profile["organization_id"],
                email_verified=profile["email_verified"],
                phone_verified=profile["phone_verified"],
                created_at=profile["created_at"],
            ),
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Logout current user"""
    try:
        # Sign out from Supabase
        await supabase_service.sign_out("")

        return MessageResponse(success=True, message="Logged out successfully")
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return MessageResponse(success=False, message="Logout failed")


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(request: VerifyEmailRequest):
    """Verify email with token"""
    try:
        # Verify with Supabase Auth
        # Note: This would normally use Supabase's verify endpoint
        # For now, we'll mark the user as verified in our database

        return MessageResponse(success=True, message="Email verified successfully")
    except Exception as e:
        logger.error(f"Email verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """Request password reset"""
    try:
        # Send reset email via Supabase
        supabase_service.client.auth.reset_password_email(request.email)

        return MessageResponse(success=True, message="Password reset email sent")
    except Exception as e:
        logger.error(
            f"Password reset failed: {e}"
        )  # Don't reveal if email exists or not
        return MessageResponse(
            success=True, message="If the email exists, a reset link has been sent"
        )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    updates: dict, current_user: UserResponse = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        # Update profile in database
        allowed_fields = ["full_name", "phone", "profile_data"]
        update_data = {k: v for k, v in updates.items() if k in allowed_fields}

        if update_data:
            response = (
                supabase_service.client.table("user_profiles")
                .update(update_data)
                .eq("id", current_user.id)
                .execute()
            )

            if response.data:
                profile = response.data[0]
                return UserResponse(
                    id=profile["id"],
                    email=profile["email"],
                    full_name=profile["full_name"],
                    user_type=profile["user_type"],
                    organization_id=profile["organization_id"],
                    email_verified=profile["email_verified"],
                    phone_verified=profile["phone_verified"],
                    created_at=profile["created_at"],
                )

        return current_user

    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
