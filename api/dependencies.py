"""Common dependencies for API endpoints."""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime

from api.config import settings
from api.models.user import User
from api.services.supabase import supabase_service

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        
        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        # Get user from database
        supabase = supabase_service.client
        result = supabase.table('user_profiles').select('*').eq(
            'id', user_id
        ).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = result.data[0]
        
        # Create User model
        return User(
            id=UUID(user_data['id']),
            email=user_data['email'],
            full_name=user_data.get('full_name'),
            role=user_data['role'],
            organization_id=UUID(user_data['organization_id']) if user_data.get('organization_id') else None,
            is_active=user_data.get('is_active', True),
            created_at=user_data['created_at'],
            updated_at=user_data['updated_at']
        )
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate user: {str(e)}"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure the current user is an admin."""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_manager_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure the current user is at least a manager."""
    if current_user.role not in ['admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin privileges required"
        )
    return current_user

async def get_organization_id(
    current_user: User = Depends(get_current_user)
) -> UUID:
    """Get the organization ID for the current user."""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an organization"
        )
    return current_user.organization_id

class RoleChecker:
    """Dependency class for checking user roles."""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of the following roles: {', '.join(self.allowed_roles)}"
            )
        return current_user

# Role-based dependency instances
require_admin = RoleChecker(['admin'])
require_manager = RoleChecker(['admin', 'manager'])
require_contractor = RoleChecker(['admin', 'manager', 'contractor'])

class PaginationParams:
    """Common pagination parameters."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be 1 or greater"
            )
        if per_page < 1 or per_page > max_per_page:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Per page must be between 1 and {max_per_page}"
            )
        
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page