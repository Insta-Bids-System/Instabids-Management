"""Property models for API validation and serialization."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, validator
import re

class PropertyType(str, Enum):
    """Property type enumeration."""
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    COMMERCIAL_OFFICE = "commercial_office"
    COMMERCIAL_RETAIL = "commercial_retail"
    COMMERCIAL_INDUSTRIAL = "commercial_industrial"
    MIXED_USE = "mixed_use"
    OTHER = "other"

class PropertyStatus(str, Enum):
    """Property status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class PropertyDetails(BaseModel):
    """Detailed property information."""
    square_footage: Optional[int] = Field(None, gt=0, le=1000000)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    units: Optional[int] = Field(None, ge=1, le=1000)
    floors: Optional[int] = Field(None, ge=1, le=200)
    parking_spaces: Optional[int] = Field(None, ge=0, le=1000)
    lot_size: Optional[float] = Field(None, gt=0)
    
    @validator('year_built')
    def validate_year_built(cls, v):
        if v and v > datetime.now().year:
            raise ValueError('Year built cannot be in the future')
        return v

class PropertyPhoto(BaseModel):
    """Property photo metadata."""
    url: str
    caption: Optional[str] = None
    is_primary: bool = False
    uploaded_at: datetime = Field(default_factory=datetime.now)

class PropertyCoordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class PropertyBase(BaseModel):
    """Base property model with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    zip: str = Field(..., min_length=5, max_length=20)
    country: str = Field(default="USA", max_length=100)
    property_type: PropertyType = PropertyType.OTHER
    status: PropertyStatus = PropertyStatus.ACTIVE
    manager_id: Optional[UUID] = None
    details: PropertyDetails = Field(default_factory=PropertyDetails)
    amenities: List[str] = Field(default_factory=list)
    coordinates: Optional[PropertyCoordinates] = None
    photos: List[PropertyPhoto] = Field(default_factory=list)
    
    @validator('zip')
    def validate_zip(cls, v):
        # Basic US ZIP code validation
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid ZIP code format')
        return v
    
    @validator('amenities')
    def validate_amenities(cls, v):
        # Limit amenities and ensure uniqueness
        if len(v) > 50:
            raise ValueError('Too many amenities (max 50)')
        return list(set(v))  # Remove duplicates
    
    @validator('photos')
    def validate_photos(cls, v):
        # Ensure only one primary photo
        primary_count = sum(1 for photo in v if photo.is_primary)
        if primary_count > 1:
            raise ValueError('Only one photo can be marked as primary')
        return v

class PropertyCreate(PropertyBase):
    """Model for creating a new property."""
    organization_id: UUID

class PropertyUpdate(BaseModel):
    """Model for updating an existing property."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=50)
    zip: Optional[str] = Field(None, min_length=5, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    manager_id: Optional[UUID] = None
    details: Optional[PropertyDetails] = None
    amenities: Optional[List[str]] = None
    coordinates: Optional[PropertyCoordinates] = None
    photos: Optional[List[PropertyPhoto]] = None

class Property(PropertyBase):
    """Complete property model with all fields."""
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class PropertyFilter(BaseModel):
    """Filters for property queries."""
    search: Optional[str] = None
    property_type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    manager_id: Optional[UUID] = None
    city: Optional[str] = None
    state: Optional[str] = None
    min_square_footage: Optional[int] = None
    max_square_footage: Optional[int] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    amenities: Optional[List[str]] = None
    group_id: Optional[UUID] = None
    include_archived: bool = False

class PropertyBulkCreate(BaseModel):
    """Model for bulk property creation."""
    properties: List[PropertyCreate]
    skip_duplicates: bool = True
    
    @validator('properties')
    def validate_property_count(cls, v):
        if len(v) > 100:
            raise ValueError('Cannot create more than 100 properties at once')
        if len(v) == 0:
            raise ValueError('At least one property is required')
        return v

class PropertyImport(BaseModel):
    """Model for property import."""
    file_type: str = Field(..., regex="^(csv|xlsx)$")
    mapping: Dict[str, str]
    skip_errors: bool = True
    dry_run: bool = False

class PropertyExport(BaseModel):
    """Model for property export."""
    format: str = Field(..., regex="^(csv|xlsx|json)$")
    filters: Optional[PropertyFilter] = None
    include_deleted: bool = False

# Property Group Models

class PropertyGroupBase(BaseModel):
    """Base property group model."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class PropertyGroupCreate(PropertyGroupBase):
    """Model for creating a property group."""
    organization_id: UUID
    property_ids: List[UUID] = Field(default_factory=list)

class PropertyGroupUpdate(BaseModel):
    """Model for updating a property group."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class PropertyGroup(PropertyGroupBase):
    """Complete property group model."""
    id: UUID
    organization_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    property_count: int = 0
    
    class Config:
        orm_mode = True

class PropertyGroupMemberAction(BaseModel):
    """Model for adding/removing properties from groups."""
    property_ids: List[UUID]
    
    @validator('property_ids')
    def validate_property_ids(cls, v):
        if len(v) > 100:
            raise ValueError('Cannot modify more than 100 properties at once')
        if len(v) == 0:
            raise ValueError('At least one property ID is required')
        return list(set(v))  # Remove duplicates

# Response Models

class PropertyListResponse(BaseModel):
    """Response for property list endpoint."""
    properties: List[Property]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class PropertyGroupListResponse(BaseModel):
    """Response for property group list endpoint."""
    groups: List[PropertyGroup]
    total: int

class PropertyBulkResponse(BaseModel):
    """Response for bulk operations."""
    successful: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    created_ids: List[UUID] = Field(default_factory=list)

class PropertyImportResponse(BaseModel):
    """Response for import operations."""
    total_rows: int
    imported: int
    skipped: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    preview: Optional[List[Property]] = None