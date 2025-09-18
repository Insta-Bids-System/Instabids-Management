"""User models used for authentication context within the API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """Representation of an authenticated user returned by dependencies."""

    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    organization_id: Optional[UUID] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


__all__ = ["User"]
