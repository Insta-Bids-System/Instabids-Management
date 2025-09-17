# Contractor Onboarding Technical Implementation Plan

## Overview

This document outlines the technical implementation plan for the contractor onboarding feature in the InstaBids marketplace platform. The plan extends the existing authentication system to support comprehensive contractor profiles while maintaining security and ensuring fast, accurate matching for project invitations.

## Table of Contents

1. [Database Design](#database-design)
2. [API Design](#api-design)
3. [Frontend Components](#frontend-components)
4. [Verification System](#verification-system)
5. [Matching Algorithm](#matching-algorithm)
6. [Implementation Order](#implementation-order)

---

## Database Design

### Overview

The database design extends the existing `contractors` table and adds new tables to support the comprehensive contractor onboarding process while maintaining compatibility with the current bid card and matching systems.

### Core Tables

#### 1. Extended `contractors` Table

```sql
-- Extend existing contractors table with onboarding fields
ALTER TABLE contractors ADD COLUMN IF NOT EXISTS
  -- Business Information
  business_type TEXT CHECK (business_type IN ('sole_proprietor', 'llc', 'corporation', 'partnership')),
  years_in_business INTEGER,
  number_of_employees INTEGER,
  business_address JSONB, -- {street, city, state, zip, coordinates}
  website_url TEXT,
  business_description TEXT,
  
  -- Profile Media
  company_logo_url TEXT,
  cover_photo_url TEXT,
  
  -- Verification Status
  verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('pending', 'additional_info_required', 'verified', 'rejected', 'suspended')),
  verification_notes TEXT,
  verification_date TIMESTAMP,
  verified_by UUID, -- Admin user ID
  
  -- Profile Completion
  profile_completion_percentage INTEGER DEFAULT 0,
  onboarding_completed_at TIMESTAMP,
  
  -- Preferences
  emergency_available BOOLEAN DEFAULT false,
  emergency_response_time_hours INTEGER,
  emergency_fee_multiplier DECIMAL(3,2) DEFAULT 1.0,
  minimum_notice_hours INTEGER DEFAULT 24,
  booking_window_days INTEGER DEFAULT 30,
  
  -- Business Metrics
  awards_and_recognition TEXT[],
  mission_statement TEXT,
  
  -- Updated tracking
  profile_updated_at TIMESTAMP DEFAULT NOW();

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_contractors_verification_status ON contractors (verification_status);
CREATE INDEX IF NOT EXISTS idx_contractors_business_type ON contractors (business_type);
CREATE INDEX IF NOT EXISTS idx_contractors_emergency_available ON contractors (emergency_available);
CREATE INDEX IF NOT EXISTS idx_contractors_profile_completion ON contractors (profile_completion_percentage);
```

#### 2. Contractor Credentials Table

```sql
CREATE TABLE contractor_credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  credential_type TEXT NOT NULL CHECK (credential_type IN ('business_license', 'insurance', 'trade_certification', 'manufacturer_certification', 'safety_certification')),
  
  -- License/Certificate Details
  license_number TEXT,
  issuing_authority TEXT,
  coverage_amount DECIMAL(12,2), -- For insurance
  carrier_name TEXT, -- For insurance
  
  -- File Information
  document_url TEXT NOT NULL,
  document_filename TEXT,
  document_size_bytes INTEGER,
  document_mime_type TEXT,
  
  -- Validity
  issue_date DATE,
  expiration_date DATE,
  is_expired BOOLEAN GENERATED ALWAYS AS (expiration_date < CURRENT_DATE) STORED,
  
  -- Verification
  verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected', 'expired')),
  verification_date TIMESTAMP,
  verification_notes TEXT,
  verified_by UUID, -- Admin user ID
  
  -- Tracking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(contractor_id, credential_type, license_number)
);

-- Indexes
CREATE INDEX idx_credentials_contractor_id ON contractor_credentials (contractor_id);
CREATE INDEX idx_credentials_type ON contractor_credentials (credential_type);
CREATE INDEX idx_credentials_verification_status ON contractor_credentials (verification_status);
CREATE INDEX idx_credentials_expiration ON contractor_credentials (expiration_date) WHERE expiration_date IS NOT NULL;
```

#### 3. Contractor Service Areas Table

```sql
CREATE TABLE contractor_service_areas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  
  -- Service Area Definition
  area_type TEXT NOT NULL CHECK (area_type IN ('zip_codes', 'radius', 'cities_counties')),
  
  -- ZIP Code Service Area
  zip_codes TEXT[], -- For zip_codes type
  
  -- Radius Service Area
  center_address JSONB, -- {street, city, state, zip, coordinates}
  radius_miles INTEGER, -- For radius type
  
  -- Cities/Counties Service Area
  cities TEXT[], -- For cities_counties type
  counties TEXT[], -- For cities_counties type
  states TEXT[], -- For multi-state contractors
  
  -- Travel & Pricing
  max_travel_distance_miles INTEGER,
  travel_fee_per_mile DECIMAL(5,2),
  minimum_travel_fee DECIMAL(8,2),
  
  -- Tracking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_service_areas_contractor_id ON contractor_service_areas (contractor_id);
CREATE INDEX idx_service_areas_zip_codes ON contractor_service_areas USING GIN (zip_codes);
CREATE INDEX idx_service_areas_cities ON contractor_service_areas USING GIN (cities);
CREATE INDEX idx_service_areas_counties ON contractor_service_areas USING GIN (counties);
```

#### 4. Contractor Availability Table

```sql
CREATE TABLE contractor_availability (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  
  -- Regular Hours
  monday_start TIME,
  monday_end TIME,
  tuesday_start TIME,
  tuesday_end TIME,
  wednesday_start TIME,
  wednesday_end TIME,
  thursday_start TIME,
  thursday_end TIME,
  friday_start TIME,
  friday_end TIME,
  saturday_start TIME,
  saturday_end TIME,
  sunday_start TIME,
  sunday_end TIME,
  
  -- Holiday Availability
  holiday_available BOOLEAN DEFAULT false,
  
  -- Blackout Dates
  blackout_dates JSONB, -- [{start: "2024-12-24", end: "2024-12-26", reason: "Christmas"}]
  
  -- Capacity Management
  max_jobs_per_week INTEGER DEFAULT 10,
  current_job_count INTEGER DEFAULT 0,
  
  -- Tracking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(contractor_id)
);

-- Indexes
CREATE INDEX idx_availability_contractor_id ON contractor_availability (contractor_id);
```

#### 5. Contractor Portfolio Table

```sql
CREATE TABLE contractor_portfolio (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  
  -- Project Information
  project_title TEXT NOT NULL,
  project_description TEXT,
  project_category TEXT, -- kitchen, bathroom, roofing, etc.
  
  -- Project Details
  project_size_sqft INTEGER,
  project_budget_range TEXT, -- "$5,000-$10,000"
  completion_date DATE,
  
  -- Media
  before_image_urls TEXT[],
  after_image_urls TEXT[],
  
  -- Customer Information (optional)
  customer_testimonial TEXT,
  customer_rating INTEGER CHECK (customer_rating >= 1 AND customer_rating <= 5),
  customer_name TEXT,
  customer_location TEXT, -- City, State only for privacy
  
  -- Visibility
  is_featured BOOLEAN DEFAULT false,
  display_order INTEGER DEFAULT 0,
  
  -- Tracking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_portfolio_contractor_id ON contractor_portfolio (contractor_id);
CREATE INDEX idx_portfolio_category ON contractor_portfolio (project_category);
CREATE INDEX idx_portfolio_featured ON contractor_portfolio (is_featured, display_order);
```

#### 6. Contractor Job Preferences Table

```sql
CREATE TABLE contractor_job_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  
  -- Job Size Preferences
  minimum_job_size_dollars INTEGER DEFAULT 1000,
  maximum_job_size_dollars INTEGER,
  preferred_job_size_range JSONB, -- {min: 5000, max: 25000}
  
  -- Property Types
  serves_residential BOOLEAN DEFAULT true,
  serves_commercial BOOLEAN DEFAULT false,
  serves_multifamily BOOLEAN DEFAULT false,
  serves_hoa_condo BOOLEAN DEFAULT false,
  
  -- Service Types
  offers_emergency_repairs BOOLEAN DEFAULT false,
  offers_preventive_maintenance BOOLEAN DEFAULT true,
  offers_new_installations BOOLEAN DEFAULT true,
  offers_renovations BOOLEAN DEFAULT true,
  offers_inspections BOOLEAN DEFAULT false,
  
  -- Excluded Job Types
  excluded_job_types TEXT[], -- ["flood_damage", "fire_damage", "mold_remediation"]
  
  -- Budget Preferences
  accepted_budget_ranges JSONB, -- [{"min": 1000, "max": 5000}, {"min": 10000, "max": 25000}]
  
  -- Tracking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(contractor_id)
);

-- Indexes
CREATE INDEX idx_job_preferences_contractor_id ON contractor_job_preferences (contractor_id);
CREATE INDEX idx_job_preferences_emergency ON contractor_job_preferences (offers_emergency_repairs);
```

#### 7. Contractor Performance Metrics Table

```sql
CREATE TABLE contractor_performance_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  
  -- Performance Stats
  total_jobs_completed INTEGER DEFAULT 0,
  total_jobs_awarded INTEGER DEFAULT 0,
  total_invitations_received INTEGER DEFAULT 0,
  total_bids_submitted INTEGER DEFAULT 0,
  
  -- Response Metrics
  average_response_time_hours DECIMAL(8,2),
  response_rate_percentage DECIMAL(5,2), -- 0.00 to 100.00
  
  -- Quality Metrics
  average_customer_rating DECIMAL(3,2), -- 0.00 to 5.00
  on_time_completion_rate DECIMAL(5,2), -- 0.00 to 100.00
  customer_satisfaction_score DECIMAL(5,2), -- 0.00 to 100.00
  
  -- Financial Metrics
  total_revenue DECIMAL(12,2) DEFAULT 0,
  average_job_value DECIMAL(10,2),
  
  -- Tracking
  last_calculated_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(contractor_id)
);

-- Indexes
CREATE INDEX idx_performance_contractor_id ON contractor_performance_metrics (contractor_id);
CREATE INDEX idx_performance_rating ON contractor_performance_metrics (average_customer_rating DESC);
CREATE INDEX idx_performance_response_rate ON contractor_performance_metrics (response_rate_percentage DESC);
```

#### 8. Verification Queue Table

```sql
CREATE TABLE contractor_verification_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
  
  -- Queue Information
  queue_type TEXT NOT NULL CHECK (queue_type IN ('initial_review', 'credential_expiry', 'manual_review', 'appeal')),
  priority INTEGER DEFAULT 3 CHECK (priority >= 1 AND priority <= 5), -- 1 = highest priority
  
  -- Review Details
  review_status TEXT DEFAULT 'pending' CHECK (review_status IN ('pending', 'in_progress', 'completed', 'escalated')),
  assigned_to UUID, -- Admin user ID
  review_notes TEXT,
  
  -- Automation Results
  automated_checks_results JSONB, -- Results from automated verification APIs
  automated_checks_passed BOOLEAN,
  
  -- Timing
  submitted_at TIMESTAMP DEFAULT NOW(),
  assigned_at TIMESTAMP,
  completed_at TIMESTAMP,
  due_date TIMESTAMP,
  
  -- Tracking
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_verification_queue_status ON contractor_verification_queue (review_status, priority);
CREATE INDEX idx_verification_queue_contractor ON contractor_verification_queue (contractor_id);
CREATE INDEX idx_verification_queue_assigned ON contractor_verification_queue (assigned_to);
CREATE INDEX idx_verification_queue_due_date ON contractor_verification_queue (due_date);
```

### Database Triggers and Functions

```sql
-- Update contractor profile completion percentage
CREATE OR REPLACE FUNCTION calculate_contractor_profile_completion(contractor_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
  completion_percentage INTEGER := 0;
  total_fields INTEGER := 20; -- Total scoreable fields
  completed_fields INTEGER := 0;
BEGIN
  -- Basic information (5 fields)
  SELECT completed_fields + (
    CASE WHEN company_name IS NOT NULL AND company_name != '' THEN 1 ELSE 0 END +
    CASE WHEN contact_name IS NOT NULL AND contact_name != '' THEN 1 ELSE 0 END +
    CASE WHEN email IS NOT NULL AND email != '' THEN 1 ELSE 0 END +
    CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 ELSE 0 END +
    CASE WHEN business_type IS NOT NULL THEN 1 ELSE 0 END
  ) INTO completed_fields
  FROM contractors WHERE id = contractor_uuid;
  
  -- Credentials (minimum license + insurance = 2 fields)
  SELECT completed_fields + (
    CASE WHEN EXISTS(
      SELECT 1 FROM contractor_credentials 
      WHERE contractor_id = contractor_uuid 
      AND credential_type = 'business_license' 
      AND verification_status = 'verified'
    ) THEN 1 ELSE 0 END +
    CASE WHEN EXISTS(
      SELECT 1 FROM contractor_credentials 
      WHERE contractor_id = contractor_uuid 
      AND credential_type = 'insurance' 
      AND verification_status = 'verified'
    ) THEN 1 ELSE 0 END
  ) INTO completed_fields;
  
  -- Service areas (1 field)
  SELECT completed_fields + (
    CASE WHEN EXISTS(
      SELECT 1 FROM contractor_service_areas 
      WHERE contractor_id = contractor_uuid
    ) THEN 1 ELSE 0 END
  ) INTO completed_fields;
  
  -- Additional fields can be added here...
  
  completion_percentage := (completed_fields * 100 / total_fields);
  
  -- Update the contractor record
  UPDATE contractors 
  SET profile_completion_percentage = completion_percentage,
      profile_updated_at = NOW()
  WHERE id = contractor_uuid;
  
  RETURN completion_percentage;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update profile completion on changes
CREATE OR REPLACE FUNCTION trigger_update_profile_completion()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM calculate_contractor_profile_completion(NEW.contractor_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for relevant tables
CREATE TRIGGER update_completion_on_credentials
  AFTER INSERT OR UPDATE OR DELETE ON contractor_credentials
  FOR EACH ROW EXECUTE FUNCTION trigger_update_profile_completion();

CREATE TRIGGER update_completion_on_service_areas
  AFTER INSERT OR UPDATE OR DELETE ON contractor_service_areas
  FOR EACH ROW EXECUTE FUNCTION trigger_update_profile_completion();
```

---

## API Design

### Overview

The API design extends the existing FastAPI backend with new endpoints for contractor onboarding, profile management, and verification workflows.

### Authentication & Authorization

```python
# auth/contractor_auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any

security = HTTPBearer()

async def get_current_contractor(token: str = Depends(security)) -> Dict[str, Any]:
    """
    Get current authenticated contractor from JWT token
    Validates token and returns contractor profile
    """
    try:
        # Validate JWT token using existing auth system
        user_data = validate_jwt_token(token.credentials)
        
        # Get contractor profile from database
        contractor = await db.get_contractor_by_user_id(user_data["user_id"])
        
        if not contractor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contractor profile not found"
            )
        
        return contractor
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_current_contractor_optional(
    token: Optional[str] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Optional contractor authentication for public endpoints"""
    if not token:
        return None
    return await get_current_contractor(token)
```

### Core API Endpoints

#### 1. Registration and Onboarding Endpoints

```python
# routers/contractor_onboarding_api.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

router = APIRouter(prefix="/api/contractor/onboarding", tags=["contractor-onboarding"])

class BusinessType(str, Enum):
    SOLE_PROPRIETOR = "sole_proprietor"
    LLC = "llc"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"

class ContractorRegistrationRequest(BaseModel):
    # Basic Information
    business_name: str
    contact_name: str
    email: EmailStr
    phone: str
    business_type: BusinessType
    
    # Business Details
    years_in_business: Optional[int] = None
    number_of_employees: Optional[int] = None
    business_address: Optional[Dict[str, Any]] = None
    website_url: Optional[str] = None
    business_description: Optional[str] = None

@router.post("/register")
async def register_contractor(
    registration_data: ContractorRegistrationRequest,
    db: SupabaseDB = Depends(get_database)
):
    """
    Step 1: Register new contractor with basic information
    Creates user account and contractor profile
    """
    try:
        # Create user account in auth system
        auth_user = await create_auth_user(
            email=registration_data.email,
            password=generate_temp_password(),  # Send via email
            user_type="contractor"
        )
        
        # Create contractor profile
        contractor_data = {
            "user_id": auth_user["id"],
            "company_name": registration_data.business_name,
            "contact_name": registration_data.contact_name,
            "email": registration_data.email,
            "phone": registration_data.phone,
            "business_type": registration_data.business_type,
            "years_in_business": registration_data.years_in_business,
            "number_of_employees": registration_data.number_of_employees,
            "business_address": registration_data.business_address,
            "website_url": registration_data.website_url,
            "business_description": registration_data.business_description,
            "verification_status": "pending",
            "onboarded": False
        }
        
        contractor = await db.create_contractor(contractor_data)
        
        # Calculate initial profile completion
        completion = await calculate_profile_completion(contractor["id"])
        
        # Send welcome email with login credentials
        await send_contractor_welcome_email(
            email=registration_data.email,
            name=registration_data.contact_name,
            temp_password=temp_password
        )
        
        return {
            "success": True,
            "contractor_id": contractor["id"],
            "profile_completion": completion,
            "next_step": "upload_credentials"
        }
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed. Please try again."
        )

class CredentialUploadRequest(BaseModel):
    contractor_id: str
    credential_type: str
    license_number: Optional[str] = None
    issuing_authority: Optional[str] = None
    coverage_amount: Optional[float] = None
    carrier_name: Optional[str] = None
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None

@router.post("/credentials/upload")
async def upload_credential(
    credential_data: CredentialUploadRequest,
    file: UploadFile = File(...),
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """
    Step 2: Upload contractor credentials (license, insurance, certifications)
    """
    try:
        # Validate file type and size
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(400, "File size too large")
        
        if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
            raise HTTPException(400, "Invalid file type")
        
        # Upload file to storage
        file_url = await upload_file_to_storage(
            file=file,
            bucket="contractor-credentials",
            path=f"{contractor['id']}/{credential_data.credential_type}"
        )
        
        # Save credential record
        credential_record = {
            "contractor_id": contractor["id"],
            "credential_type": credential_data.credential_type,
            "license_number": credential_data.license_number,
            "issuing_authority": credential_data.issuing_authority,
            "coverage_amount": credential_data.coverage_amount,
            "carrier_name": credential_data.carrier_name,
            "issue_date": credential_data.issue_date,
            "expiration_date": credential_data.expiration_date,
            "document_url": file_url,
            "document_filename": file.filename,
            "document_size_bytes": file.size,
            "document_mime_type": file.content_type,
            "verification_status": "pending"
        }
        
        credential = await db.create_contractor_credential(credential_record)
        
        # Add to verification queue
        await add_to_verification_queue(
            contractor_id=contractor["id"],
            queue_type="initial_review",
            priority=2
        )
        
        # Update profile completion
        completion = await calculate_profile_completion(contractor["id"])
        
        return {
            "success": True,
            "credential_id": credential["id"],
            "profile_completion": completion,
            "verification_status": "pending"
        }
        
    except Exception as e:
        logger.error(f"Credential upload failed: {e}")
        raise HTTPException(500, "Upload failed")
```

#### 2. Profile Management Endpoints

```python
@router.get("/profile")
async def get_contractor_profile(
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """Get complete contractor profile with all related data"""
    try:
        # Get full profile with joined data
        profile = await db.get_contractor_full_profile(contractor["id"])
        
        return {
            "contractor": profile["contractor"],
            "credentials": profile["credentials"],
            "service_areas": profile["service_areas"],
            "availability": profile["availability"],
            "portfolio": profile["portfolio"],
            "job_preferences": profile["job_preferences"],
            "performance_metrics": profile["performance_metrics"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        raise HTTPException(500, "Failed to get profile")

@router.put("/profile/basic")
async def update_basic_profile(
    updates: ContractorBasicProfileUpdate,
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """Update basic profile information"""
    try:
        updated_contractor = await db.update_contractor(
            contractor_id=contractor["id"],
            updates=updates.dict(exclude_unset=True)
        )
        
        # Recalculate profile completion
        completion = await calculate_profile_completion(contractor["id"])
        
        return {
            "success": True,
            "contractor": updated_contractor,
            "profile_completion": completion
        }
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(500, "Update failed")
```

#### 3. Service Area Management Endpoints

```python
@router.post("/service-areas")
async def create_service_area(
    service_area: ServiceAreaCreate,
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """Create new service area definition"""
    try:
        service_area_data = {
            "contractor_id": contractor["id"],
            **service_area.dict()
        }
        
        area = await db.create_service_area(service_area_data)
        
        # Update profile completion
        completion = await calculate_profile_completion(contractor["id"])
        
        return {
            "success": True,
            "service_area": area,
            "profile_completion": completion
        }
        
    except Exception as e:
        logger.error(f"Service area creation failed: {e}")
        raise HTTPException(500, "Creation failed")

@router.get("/service-areas/validate/{zip_code}")
async def validate_service_area(
    zip_code: str,
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """Check if contractor serves a specific ZIP code"""
    try:
        serves_area = await check_contractor_serves_area(
            contractor_id=contractor["id"],
            zip_code=zip_code
        )
        
        return {
            "serves_area": serves_area,
            "zip_code": zip_code
        }
        
    except Exception as e:
        logger.error(f"Area validation failed: {e}")
        raise HTTPException(500, "Validation failed")
```

#### 4. Verification Status Endpoints

```python
@router.get("/verification/status")
async def get_verification_status(
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """Get current verification status and requirements"""
    try:
        status = await db.get_contractor_verification_status(contractor["id"])
        
        return {
            "overall_status": status["verification_status"],
            "credentials": status["credentials_status"],
            "pending_items": status["pending_items"],
            "completion_percentage": status["profile_completion"],
            "next_steps": status["next_steps"]
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(500, "Status check failed")

@router.post("/verification/resubmit")
async def resubmit_for_verification(
    resubmission: VerificationResubmission,
    contractor: Dict[str, Any] = Depends(get_current_contractor)
):
    """Resubmit contractor for verification after addressing issues"""
    try:
        # Update any provided information
        if resubmission.updated_data:
            await db.update_contractor(
                contractor_id=contractor["id"],
                updates=resubmission.updated_data
            )
        
        # Reset verification status
        await db.update_contractor_verification_status(
            contractor_id=contractor["id"],
            status="pending",
            notes=resubmission.notes
        )
        
        # Add back to verification queue with high priority
        await add_to_verification_queue(
            contractor_id=contractor["id"],
            queue_type="manual_review",
            priority=1
        )
        
        return {
            "success": True,
            "message": "Resubmitted for verification",
            "estimated_review_time": "24-48 hours"
        }
        
    except Exception as e:
        logger.error(f"Resubmission failed: {e}")
        raise HTTPException(500, "Resubmission failed")
```

#### 5. Admin Verification Endpoints

```python
# routers/admin_contractor_verification.py
@router.get("/admin/verification/queue")
async def get_verification_queue(
    status: Optional[str] = None,
    priority: Optional[int] = None,
    limit: int = 50,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Get contractors pending verification"""
    try:
        queue_items = await db.get_verification_queue(
            status=status,
            priority=priority,
            limit=limit
        )
        
        return {
            "queue_items": queue_items,
            "total_pending": len([item for item in queue_items if item["review_status"] == "pending"])
        }
        
    except Exception as e:
        logger.error(f"Queue fetch failed: {e}")
        raise HTTPException(500, "Queue fetch failed")

@router.post("/admin/verification/{contractor_id}/approve")
async def approve_contractor(
    contractor_id: str,
    approval: ContractorApproval,
    admin: Dict[str, Any] = Depends(get_current_admin)
):
    """Approve contractor after verification"""
    try:
        # Update contractor status
        await db.update_contractor_verification_status(
            contractor_id=contractor_id,
            status="verified",
            notes=approval.notes,
            verified_by=admin["id"]
        )
        
        # Update verification queue
        await db.complete_verification_queue_item(
            contractor_id=contractor_id,
            completed_by=admin["id"],
            result="approved"
        )
        
        # Send approval notification
        await send_contractor_approval_email(contractor_id)
        
        return {
            "success": True,
            "message": "Contractor approved"
        }
        
    except Exception as e:
        logger.error(f"Approval failed: {e}")
        raise HTTPException(500, "Approval failed")
```

---

## Frontend Components

### Overview

The frontend implementation creates a modern, multi-step onboarding wizard and comprehensive dashboard for contractor profile management, built with React, TypeScript, and Tailwind CSS.

### Core Components Architecture

```
src/
├── components/
│   ├── contractor/
│   │   ├── onboarding/
│   │   │   ├── OnboardingWizard.tsx
│   │   │   ├── BasicInfoStep.tsx
│   │   │   ├── BusinessDetailsStep.tsx
│   │   │   ├── CredentialsUploadStep.tsx
│   │   │   ├── TradeSpecialtiesStep.tsx
│   │   │   ├── ServiceAreasStep.tsx
│   │   │   ├── AvailabilityStep.tsx
│   │   │   ├── JobPreferencesStep.tsx
│   │   │   └── ProfileSetupStep.tsx
│   │   ├── dashboard/
│   │   │   ├── ContractorDashboard.tsx
│   │   │   ├── ProfileManagement.tsx
│   │   │   ├── VerificationStatus.tsx
│   │   │   ├── PortfolioManager.tsx
│   │   │   └── PerformanceMetrics.tsx
│   │   └── profile/
│   │       ├── ProfilePreview.tsx
│   │       ├── CredentialsManager.tsx
│   │       ├── ServiceAreaManager.tsx
│   │       └── AvailabilityManager.tsx
```

### 1. Multi-Step Onboarding Wizard

```typescript
// components/contractor/onboarding/OnboardingWizard.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useContractorOnboarding } from '../../../hooks/useContractorOnboarding';
import { BasicInfoStep } from './BasicInfoStep';
import { BusinessDetailsStep } from './BusinessDetailsStep';
import { CredentialsUploadStep } from './CredentialsUploadStep';
import { TradeSpecialtiesStep } from './TradeSpecialtiesStep';
import { ServiceAreasStep } from './ServiceAreasStep';
import { AvailabilityStep } from './AvailabilityStep';
import { JobPreferencesStep } from './JobPreferencesStep';
import { ProfileSetupStep } from './ProfileSetupStep';

interface OnboardingState {
  currentStep: number;
  totalSteps: number;
  profileCompletion: number;
  contractorId?: string;
  formData: Record<string, any>;
  canProceed: boolean;
}

export const OnboardingWizard: React.FC = () => {
  const navigate = useNavigate();
  const { register, uploadCredential, updateProfile } = useContractorOnboarding();
  
  const [state, setState] = useState<OnboardingState>({
    currentStep: 1,
    totalSteps: 8,
    profileCompletion: 0,
    formData: {},
    canProceed: false
  });

  const steps = [
    { 
      id: 1, 
      title: 'Basic Information', 
      component: BasicInfoStep,
      required: true 
    },
    { 
      id: 2, 
      title: 'Business Details', 
      component: BusinessDetailsStep,
      required: false 
    },
    { 
      id: 3, 
      title: 'Upload Credentials', 
      component: CredentialsUploadStep,
      required: true 
    },
    { 
      id: 4, 
      title: 'Trade Specialties', 
      component: TradeSpecialtiesStep,
      required: true 
    },
    { 
      id: 5, 
      title: 'Service Areas', 
      component: ServiceAreasStep,
      required: true 
    },
    { 
      id: 6, 
      title: 'Availability Settings', 
      component: AvailabilityStep,
      required: true 
    },
    { 
      id: 7, 
      title: 'Job Preferences', 
      component: JobPreferencesStep,
      required: false 
    },
    { 
      id: 8, 
      title: 'Profile Setup', 
      component: ProfileSetupStep,
      required: false 
    }
  ];

  const currentStepConfig = steps.find(step => step.id === state.currentStep);
  const CurrentStepComponent = currentStepConfig?.component;

  const handleStepComplete = async (stepData: any) => {
    try {
      // Save step data
      const updatedFormData = { ...state.formData, ...stepData };
      
      // For first step, register the contractor
      if (state.currentStep === 1) {
        const result = await register(stepData);
        setState(prev => ({
          ...prev,
          contractorId: result.contractor_id,
          profileCompletion: result.profile_completion,
          formData: updatedFormData
        }));
      }
      
      // For credential upload step
      else if (state.currentStep === 3) {
        for (const credential of stepData.credentials) {
          await uploadCredential(credential);
        }
      }
      
      // For other steps, update profile
      else {
        await updateProfile(state.contractorId!, stepData);
      }
      
      // Move to next step or complete onboarding
      if (state.currentStep < state.totalSteps) {
        setState(prev => ({
          ...prev,
          currentStep: prev.currentStep + 1,
          formData: updatedFormData
        }));
      } else {
        // Onboarding complete
        navigate('/contractor/dashboard');
      }
      
    } catch (error) {
      console.error('Step completion failed:', error);
      // Handle error (show toast, etc.)
    }
  };

  const handleStepBack = () => {
    if (state.currentStep > 1) {
      setState(prev => ({
        ...prev,
        currentStep: prev.currentStep - 1
      }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Progress Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">
              Contractor Onboarding
            </h1>
            <div className="text-sm text-gray-600">
              Step {state.currentStep} of {state.totalSteps}
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(state.currentStep / state.totalSteps) * 100}%` }}
            />
          </div>
          
          {/* Profile Completion */}
          {state.profileCompletion > 0 && (
            <div className="mt-2 text-sm text-gray-600">
              Profile completion: {state.profileCompletion}%
            </div>
          )}
        </div>

        {/* Step Navigation */}
        <div className="mb-8">
          <nav className="flex space-x-4 overflow-x-auto">
            {steps.map((step) => (
              <button
                key={step.id}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap ${
                  step.id === state.currentStep
                    ? 'bg-blue-600 text-white'
                    : step.id < state.currentStep
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-500'
                }`}
                onClick={() => {
                  if (step.id < state.currentStep) {
                    setState(prev => ({ ...prev, currentStep: step.id }));
                  }
                }}
                disabled={step.id > state.currentStep}
              >
                {step.id < state.currentStep && (
                  <span className="mr-1">✓</span>
                )}
                {step.title}
                {step.required && step.id >= state.currentStep && (
                  <span className="ml-1 text-red-500">*</span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Current Step Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {CurrentStepComponent && (
            <CurrentStepComponent
              onComplete={handleStepComplete}
              onBack={handleStepBack}
              initialData={state.formData}
              canGoBack={state.currentStep > 1}
              isRequired={currentStepConfig?.required}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

### 2. Credentials Upload Component

```typescript
// components/contractor/onboarding/CredentialsUploadStep.tsx
import React, { useState } from 'react';
import { FileUploader } from '../../common/FileUploader';
import { CredentialForm } from './CredentialForm';

interface Credential {
  type: 'business_license' | 'insurance' | 'trade_certification';
  file: File;
  metadata: {
    license_number?: string;
    issuing_authority?: string;
    coverage_amount?: number;
    carrier_name?: string;
    issue_date?: string;
    expiration_date?: string;
  };
}

interface CredentialsUploadStepProps {
  onComplete: (data: { credentials: Credential[] }) => void;
  onBack: () => void;
  initialData?: any;
  canGoBack: boolean;
  isRequired: boolean;
}

export const CredentialsUploadStep: React.FC<CredentialsUploadStepProps> = ({
  onComplete,
  onBack,
  initialData,
  canGoBack,
  isRequired
}) => {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [currentCredential, setCurrentCredential] = useState<Partial<Credential>>({});
  const [isUploading, setIsUploading] = useState(false);

  const requiredCredentials = ['business_license', 'insurance'];
  const optionalCredentials = ['trade_certification'];

  const handleFileSelect = (file: File, credentialType: string) => {
    setCurrentCredential({
      type: credentialType as any,
      file,
      metadata: {}
    });
  };

  const handleCredentialMetadata = (metadata: any) => {
    if (!currentCredential.file) return;

    const newCredential: Credential = {
      type: currentCredential.type!,
      file: currentCredential.file,
      metadata
    };

    setCredentials(prev => [...prev, newCredential]);
    setCurrentCredential({});
  };

  const removeCredential = (index: number) => {
    setCredentials(prev => prev.filter((_, i) => i !== index));
  };

  const canProceed = requiredCredentials.every(type =>
    credentials.some(cred => cred.type === type)
  );

  const handleNext = () => {
    if (canProceed) {
      onComplete({ credentials });
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Upload Credentials
        </h2>
        <p className="text-gray-600">
          Upload your business license and insurance certificate. 
          Additional certifications can help improve your profile visibility.
        </p>
      </div>

      {/* Required Credentials */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Required Documents
        </h3>
        
        {requiredCredentials.map(credType => {
          const uploaded = credentials.find(c => c.type === credType);
          
          return (
            <div key={credType} className="mb-6 p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium capitalize">
                  {credType.replace('_', ' ')}
                </h4>
                {uploaded && (
                  <span className="text-green-600 text-sm">✓ Uploaded</span>
                )}
              </div>
              
              {!uploaded ? (
                <FileUploader
                  accept=".pdf,.jpg,.jpeg,.png"
                  maxSize={10 * 1024 * 1024} // 10MB
                  onFileSelect={(file) => handleFileSelect(file, credType)}
                  placeholder={`Upload ${credType.replace('_', ' ')}`}
                />
              ) : (
                <div className="flex items-center justify-between bg-gray-50 p-3 rounded">
                  <span className="text-sm text-gray-700">
                    {uploaded.file.name}
                  </span>
                  <button
                    onClick={() => removeCredential(credentials.indexOf(uploaded))}
                    className="text-red-600 hover:text-red-700 text-sm"
                  >
                    Remove
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Current Credential Form */}
      {currentCredential.file && (
        <CredentialForm
          credentialType={currentCredential.type!}
          fileName={currentCredential.file.name}
          onSubmit={handleCredentialMetadata}
          onCancel={() => setCurrentCredential({})}
        />
      )}

      {/* Uploaded Credentials Summary */}
      {credentials.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Uploaded Documents
          </h3>
          <div className="space-y-2">
            {credentials.map((credential, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div>
                  <span className="font-medium capitalize">
                    {credential.type.replace('_', ' ')}
                  </span>
                  <span className="text-gray-600 ml-2">
                    {credential.file.name}
                  </span>
                </div>
                <button
                  onClick={() => removeCredential(index)}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t">
        <button
          onClick={onBack}
          disabled={!canGoBack}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Back
        </button>
        
        <button
          onClick={handleNext}
          disabled={!canProceed}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {canProceed ? 'Continue' : 'Upload Required Documents'}
        </button>
      </div>
    </div>
  );
};
```

### 3. Service Area Manager Component

```typescript
// components/contractor/profile/ServiceAreaManager.tsx
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Circle, Marker } from 'react-leaflet';
import { useGeocoding } from '../../../hooks/useGeocoding';

interface ServiceArea {
  id?: string;
  area_type: 'zip_codes' | 'radius' | 'cities_counties';
  zip_codes?: string[];
  center_address?: any;
  radius_miles?: number;
  cities?: string[];
  counties?: string[];
  states?: string[];
  max_travel_distance_miles?: number;
  travel_fee_per_mile?: number;
  minimum_travel_fee?: number;
}

export const ServiceAreaManager: React.FC = () => {
  const [serviceAreas, setServiceAreas] = useState<ServiceArea[]>([]);
  const [activeArea, setActiveArea] = useState<ServiceArea | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const { geocodeAddress } = useGeocoding();

  const handleAddArea = () => {
    setActiveArea({
      area_type: 'radius',
      radius_miles: 25,
      max_travel_distance_miles: 50,
      travel_fee_per_mile: 0.75,
      minimum_travel_fee: 25
    });
    setIsEditing(true);
  };

  const handleSaveArea = async (area: ServiceArea) => {
    try {
      if (area.area_type === 'radius' && area.center_address) {
        // Geocode the center address
        const coordinates = await geocodeAddress(area.center_address);
        area.center_address.coordinates = coordinates;
      }

      // Save to API
      const response = await fetch('/api/contractor/service-areas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(area)
      });

      if (response.ok) {
        const savedArea = await response.json();
        setServiceAreas(prev => [...prev, savedArea.service_area]);
        setIsEditing(false);
        setActiveArea(null);
      }
    } catch (error) {
      console.error('Failed to save service area:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Service Areas</h3>
        <button
          onClick={handleAddArea}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Add Service Area
        </button>
      </div>

      {/* Service Areas List */}
      <div className="space-y-4">
        {serviceAreas.map((area, index) => (
          <ServiceAreaCard
            key={area.id || index}
            area={area}
            onEdit={() => {
              setActiveArea(area);
              setIsEditing(true);
            }}
            onDelete={() => {
              setServiceAreas(prev => prev.filter(a => a.id !== area.id));
            }}
          />
        ))}
      </div>

      {/* Service Area Editor Modal */}
      {isEditing && activeArea && (
        <ServiceAreaEditor
          area={activeArea}
          onSave={handleSaveArea}
          onCancel={() => {
            setIsEditing(false);
            setActiveArea(null);
          }}
        />
      )}
    </div>
  );
};
```

### 4. Mobile Contractor App Considerations

```typescript
// Mobile-specific components for contractor app

// components/mobile/contractor/QuickJobView.tsx
export const QuickJobView: React.FC = () => {
  return (
    <div className="mobile-job-view">
      {/* Optimized for mobile screens */}
      <div className="job-card-stack">
        {/* Swipeable job cards */}
      </div>
      <div className="quick-actions">
        {/* Accept/Decline buttons */}
      </div>
    </div>
  );
};

// components/mobile/contractor/LocationTracker.tsx
export const LocationTracker: React.FC = () => {
  // Real-time location tracking for job routing
  // Battery-optimized background tracking
  // Geofencing for automatic job status updates
};

// components/mobile/contractor/PhotoCapture.tsx
export const PhotoCapture: React.FC = () => {
  // Native camera integration
  // Automatic job site photo uploads
  // Before/after photo workflows
};
```

---

## Verification System

### Overview

The verification system provides automated and manual review processes for contractor credentials, with integration points for third-party verification services.

### Automated Verification Services

```python
# services/contractor_verification_service.py
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ContractorVerificationService:
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.verification_apis = {
            'license': LicenseVerificationAPI(),
            'insurance': InsuranceVerificationAPI(),
            'business': BusinessEntityVerificationAPI()
        }

    async def run_automated_verification(self, contractor_id: str) -> Dict[str, Any]:
        """
        Run automated verification checks for a contractor
        Returns verification results and recommendations
        """
        try:
            # Get contractor and credentials
            contractor = await self.db.get_contractor(contractor_id)
            credentials = await self.db.get_contractor_credentials(contractor_id)
            
            verification_results = {
                'contractor_id': contractor_id,
                'overall_status': 'pending',
                'checks': {},
                'recommendations': [],
                'manual_review_required': False,
                'confidence_score': 0.0
            }

            # Run parallel verification checks
            check_tasks = []
            
            # License verification
            license_creds = [c for c in credentials if c['credential_type'] == 'business_license']
            if license_creds:
                check_tasks.append(
                    self._verify_license(contractor, license_creds[0])
                )

            # Insurance verification
            insurance_creds = [c for c in credentials if c['credential_type'] == 'insurance']
            if insurance_creds:
                check_tasks.append(
                    self._verify_insurance(contractor, insurance_creds[0])
                )

            # Business entity verification
            check_tasks.append(
                self._verify_business_entity(contractor)
            )

            # Phone verification
            check_tasks.append(
                self._verify_phone_number(contractor['phone'])
            )

            # Email verification
            check_tasks.append(
                self._verify_email_domain(contractor['email'])
            )

            # Execute all checks
            check_results = await asyncio.gather(*check_tasks, return_exceptions=True)
            
            # Process results
            total_checks = 0
            passed_checks = 0
            
            for result in check_results:
                if isinstance(result, Exception):
                    logger.error(f"Verification check failed: {result}")
                    continue
                
                check_name = result['check_type']
                verification_results['checks'][check_name] = result
                
                total_checks += 1
                if result['status'] == 'verified':
                    passed_checks += 1
                elif result['status'] == 'requires_manual_review':
                    verification_results['manual_review_required'] = True

            # Calculate confidence score
            if total_checks > 0:
                verification_results['confidence_score'] = passed_checks / total_checks

            # Determine overall status
            if verification_results['confidence_score'] >= 0.8 and not verification_results['manual_review_required']:
                verification_results['overall_status'] = 'auto_approved'
            elif verification_results['confidence_score'] >= 0.6:
                verification_results['overall_status'] = 'manual_review_recommended'
            else:
                verification_results['overall_status'] = 'requires_manual_review'
                verification_results['manual_review_required'] = True

            # Generate recommendations
            verification_results['recommendations'] = self._generate_recommendations(verification_results)

            # Save results
            await self._save_verification_results(contractor_id, verification_results)

            return verification_results

        except Exception as e:
            logger.error(f"Automated verification failed for contractor {contractor_id}: {e}")
            raise

    async def _verify_license(self, contractor: Dict, license_credential: Dict) -> Dict[str, Any]:
        """Verify business license through state API"""
        try:
            state = contractor.get('business_address', {}).get('state')
            license_number = license_credential['license_number']
            
            if not state or not license_number:
                return {
                    'check_type': 'license',
                    'status': 'requires_manual_review',
                    'reason': 'Missing state or license number'
                }

            # Call state licensing API
            api_result = await self.verification_apis['license'].verify_license(
                state=state,
                license_number=license_number,
                business_name=contractor['company_name']
            )

            if api_result['valid']:
                # Check expiration
                expiry_date = license_credential.get('expiration_date')
                if expiry_date:
                    expiry = datetime.fromisoformat(expiry_date).date()
                    if expiry <= datetime.now().date():
                        return {
                            'check_type': 'license',
                            'status': 'expired',
                            'expiry_date': expiry_date,
                            'api_response': api_result
                        }

                return {
                    'check_type': 'license',
                    'status': 'verified',
                    'api_response': api_result,
                    'verified_at': datetime.now().isoformat()
                }
            else:
                return {
                    'check_type': 'license',
                    'status': 'invalid',
                    'reason': api_result.get('reason', 'License not found'),
                    'api_response': api_result
                }

        except Exception as e:
            logger.error(f"License verification failed: {e}")
            return {
                'check_type': 'license',
                'status': 'requires_manual_review',
                'reason': f'API error: {str(e)}'
            }

    async def _verify_insurance(self, contractor: Dict, insurance_credential: Dict) -> Dict[str, Any]:
        """Verify insurance certificate"""
        try:
            carrier_name = insurance_credential.get('carrier_name')
            coverage_amount = insurance_credential.get('coverage_amount')
            
            if not carrier_name or not coverage_amount:
                return {
                    'check_type': 'insurance',
                    'status': 'requires_manual_review',
                    'reason': 'Missing carrier or coverage information'
                }

            # Check if carrier is known/valid
            api_result = await self.verification_apis['insurance'].verify_carrier(carrier_name)
            
            if not api_result['valid_carrier']:
                return {
                    'check_type': 'insurance',
                    'status': 'requires_manual_review',
                    'reason': 'Unknown insurance carrier',
                    'carrier_name': carrier_name
                }

            # Check minimum coverage requirements
            state = contractor.get('business_address', {}).get('state')
            min_coverage = await self._get_minimum_coverage_requirement(state)
            
            if coverage_amount < min_coverage:
                return {
                    'check_type': 'insurance',
                    'status': 'insufficient_coverage',
                    'required_coverage': min_coverage,
                    'current_coverage': coverage_amount
                }

            # Check expiration
            expiry_date = insurance_credential.get('expiration_date')
            if expiry_date:
                expiry = datetime.fromisoformat(expiry_date).date()
                if expiry <= datetime.now().date():
                    return {
                        'check_type': 'insurance',
                        'status': 'expired',
                        'expiry_date': expiry_date
                    }

            return {
                'check_type': 'insurance',
                'status': 'verified',
                'verified_at': datetime.now().isoformat(),
                'carrier_verification': api_result
            }

        except Exception as e:
            logger.error(f"Insurance verification failed: {e}")
            return {
                'check_type': 'insurance',
                'status': 'requires_manual_review',
                'reason': f'Verification error: {str(e)}'
            }

    async def _verify_business_entity(self, contractor: Dict) -> Dict[str, Any]:
        """Verify business entity registration"""
        try:
            business_name = contractor['company_name']
            state = contractor.get('business_address', {}).get('state')
            business_type = contractor.get('business_type')

            if not state:
                return {
                    'check_type': 'business_entity',
                    'status': 'requires_manual_review',
                    'reason': 'No business address provided'
                }

            # Search business entity database
            api_result = await self.verification_apis['business'].search_business_entity(
                name=business_name,
                state=state,
                entity_type=business_type
            )

            if api_result['found']:
                entity = api_result['entity']
                
                # Check if active
                if entity.get('status') != 'active':
                    return {
                        'check_type': 'business_entity',
                        'status': 'inactive',
                        'entity_status': entity.get('status'),
                        'api_response': api_result
                    }

                return {
                    'check_type': 'business_entity',
                    'status': 'verified',
                    'entity_info': entity,
                    'verified_at': datetime.now().isoformat()
                }
            else:
                return {
                    'check_type': 'business_entity',
                    'status': 'not_found',
                    'search_terms': {
                        'name': business_name,
                        'state': state,
                        'type': business_type
                    }
                }

        except Exception as e:
            logger.error(f"Business entity verification failed: {e}")
            return {
                'check_type': 'business_entity',
                'status': 'requires_manual_review',
                'reason': f'Search error: {str(e)}'
            }

    def _generate_recommendations(self, verification_results: Dict) -> List[str]:
        """Generate actionable recommendations based on verification results"""
        recommendations = []
        
        for check_name, check_result in verification_results['checks'].items():
            status = check_result['status']
            
            if status == 'expired':
                if check_name == 'license':
                    recommendations.append("Business license has expired. Please upload renewed license.")
                elif check_name == 'insurance':
                    recommendations.append("Insurance certificate has expired. Please upload current certificate.")
                    
            elif status == 'insufficient_coverage':
                min_coverage = check_result.get('required_coverage', 'state minimum')
                recommendations.append(f"Insurance coverage below state minimum. Increase to at least ${min_coverage:,.2f}.")
                
            elif status == 'not_found':
                if check_name == 'business_entity':
                    recommendations.append("Business entity not found in state records. Verify business registration.")
                    
            elif status == 'invalid':
                if check_name == 'license':
                    recommendations.append("License number not found in state database. Verify license number.")

        if verification_results['confidence_score'] < 0.6:
            recommendations.append("Multiple verification issues found. Manual review recommended.")

        return recommendations

    async def schedule_credential_expiry_monitoring(self) -> None:
        """Schedule monitoring for credential expiration"""
        try:
            # Get all verified contractors with expiring credentials (next 30 days)
            expiring_credentials = await self.db.get_expiring_credentials(days_ahead=30)
            
            for credential in expiring_credentials:
                # Create notification for contractor
                await self._create_expiry_notification(credential)
                
                # Add to verification queue if expiring soon (next 7 days)
                if credential['days_until_expiry'] <= 7:
                    await self.db.add_to_verification_queue(
                        contractor_id=credential['contractor_id'],
                        queue_type='credential_expiry',
                        priority=2,
                        due_date=credential['expiration_date']
                    )

        except Exception as e:
            logger.error(f"Credential monitoring failed: {e}")
```

### Manual Review Queue System

```python
# services/manual_review_service.py
class ManualReviewService:
    def __init__(self, db: SupabaseDB):
        self.db = db

    async def assign_reviews_to_admins(self) -> None:
        """Automatically assign pending reviews to available admins"""
        try:
            # Get pending queue items
            pending_items = await self.db.get_verification_queue(
                status='pending',
                order_by='priority ASC, submitted_at ASC'
            )

            # Get available admin reviewers
            available_admins = await self.db.get_available_admin_reviewers()

            if not available_admins:
                logger.warning("No admin reviewers available")
                return

            # Distribute reviews evenly
            for i, item in enumerate(pending_items[:len(available_admins) * 3]):  # Max 3 per admin
                admin = available_admins[i % len(available_admins)]
                
                await self.db.assign_verification_review(
                    queue_item_id=item['id'],
                    admin_id=admin['id'],
                    due_date=datetime.now() + timedelta(hours=24)
                )

                # Send notification to admin
                await self._notify_admin_of_assignment(admin, item)

        except Exception as e:
            logger.error(f"Review assignment failed: {e}")

    async def escalate_overdue_reviews(self) -> None:
        """Escalate overdue reviews to senior admins"""
        try:
            overdue_items = await self.db.get_overdue_verification_items()
            
            for item in overdue_items:
                await self.db.escalate_verification_item(
                    queue_item_id=item['id'],
                    escalation_reason='Review overdue',
                    escalated_to='senior_admin'
                )

                # Notify senior admin
                await self._notify_escalation(item)

        except Exception as e:
            logger.error(f"Review escalation failed: {e}")
```

---

## Matching Algorithm

### Overview

The matching algorithm extends the existing contractor discovery system (CDA) to incorporate the new contractor profile data for more accurate and relevant job matching.

### Enhanced Matching Logic

```python
# services/enhanced_contractor_matching.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from geopy.distance import geodesic
import asyncio

@dataclass
class MatchScore:
    contractor_id: str
    total_score: float
    component_scores: Dict[str, float]
    eligibility_checks: Dict[str, bool]
    match_reasons: List[str]
    disqualification_reasons: List[str]

class EnhancedContractorMatching:
    def __init__(self, db: SupabaseDB):
        self.db = db
        self.scoring_weights = {
            'specialty_match': 0.25,
            'location_proximity': 0.20,
            'availability': 0.15,
            'experience_rating': 0.15,
            'job_size_preference': 0.10,
            'response_rate': 0.10,
            'emergency_capability': 0.05
        }

    async def find_matching_contractors(
        self,
        bid_card_id: str,
        max_contractors: int = 10
    ) -> List[MatchScore]:
        """
        Find and score contractors for a bid card using enhanced matching
        """
        try:
            # Get bid card details
            bid_card = await self.db.get_bid_card_full_details(bid_card_id)
            
            if not bid_card:
                raise ValueError(f"Bid card {bid_card_id} not found")

            # Get all verified contractors
            contractors = await self.db.get_verified_contractors()
            
            # Run parallel scoring for all contractors
            scoring_tasks = [
                self._score_contractor_match(contractor, bid_card)
                for contractor in contractors
            ]
            
            match_scores = await asyncio.gather(*scoring_tasks, return_exceptions=True)
            
            # Filter out exceptions and ineligible contractors
            valid_matches = [
                score for score in match_scores
                if isinstance(score, MatchScore) and self._is_eligible(score)
            ]
            
            # Sort by total score (descending)
            valid_matches.sort(key=lambda x: x.total_score, reverse=True)
            
            # Return top matches
            return valid_matches[:max_contractors]

        except Exception as e:
            logger.error(f"Contractor matching failed for bid card {bid_card_id}: {e}")
            raise

    async def _score_contractor_match(
        self,
        contractor: Dict[str, Any],
        bid_card: Dict[str, Any]
    ) -> MatchScore:
        """Score a single contractor against a bid card"""
        
        component_scores = {}
        match_reasons = []
        disqualification_reasons = []
        eligibility_checks = {}

        # 1. Specialty Match Score
        specialty_score, specialty_reasons = await self._calculate_specialty_score(
            contractor, bid_card
        )
        component_scores['specialty_match'] = specialty_score
        match_reasons.extend(specialty_reasons)

        # 2. Location Proximity Score
        location_score, location_eligible = await self._calculate_location_score(
            contractor, bid_card
        )
        component_scores['location_proximity'] = location_score
        eligibility_checks['location_served'] = location_eligible
        
        if not location_eligible:
            disqualification_reasons.append("Property outside service area")

        # 3. Availability Score
        availability_score, availability_eligible = await self._calculate_availability_score(
            contractor, bid_card
        )
        component_scores['availability'] = availability_score
        eligibility_checks['availability'] = availability_eligible
        
        if not availability_eligible:
            disqualification_reasons.append("Not available for project timeline")

        # 4. Experience & Rating Score
        experience_score = await self._calculate_experience_score(contractor, bid_card)
        component_scores['experience_rating'] = experience_score

        # 5. Job Size Preference Score
        job_size_score, size_eligible = await self._calculate_job_size_score(
            contractor, bid_card
        )
        component_scores['job_size_preference'] = job_size_score
        eligibility_checks['job_size_acceptable'] = size_eligible
        
        if not size_eligible:
            disqualification_reasons.append("Job size outside preferences")

        # 6. Response Rate Score
        response_score = await self._calculate_response_rate_score(contractor)
        component_scores['response_rate'] = response_score

        # 7. Emergency Capability Score
        emergency_score = await self._calculate_emergency_score(contractor, bid_card)
        component_scores['emergency_capability'] = emergency_score

        # Calculate weighted total score
        total_score = sum(
            component_scores[component] * self.scoring_weights[component]
            for component in component_scores
        )

        return MatchScore(
            contractor_id=contractor['id'],
            total_score=total_score,
            component_scores=component_scores,
            eligibility_checks=eligibility_checks,
            match_reasons=match_reasons,
            disqualification_reasons=disqualification_reasons
        )

    async def _calculate_specialty_score(
        self,
        contractor: Dict[str, Any],
        bid_card: Dict[str, Any]
    ) -> tuple[float, List[str]]:
        """Calculate specialty matching score"""
        reasons = []
        
        contractor_specialties = set(contractor.get('specialties', []))
        bid_card_categories = set([bid_card.get('category', '').lower()])
        
        # Add sub-categories if available
        if bid_card.get('sub_categories'):
            bid_card_categories.update(bid_card['sub_categories'])

        # Exact specialty match
        exact_matches = contractor_specialties.intersection(bid_card_categories)
        if exact_matches:
            reasons.append(f"Exact specialty match: {', '.join(exact_matches)}")
            return 1.0, reasons

        # Related specialty matching using mapping
        specialty_mapping = {
            'kitchen': ['general', 'interior'],
            'bathroom': ['plumbing', 'general', 'interior'],
            'roofing': ['general', 'exterior'],
            'landscaping': ['lawn care', 'exterior'],
            'electrical': ['general'],
            'plumbing': ['general', 'bathroom'],
            'hvac': ['general']
        }

        related_score = 0.0
        for bid_category in bid_card_categories:
            related_specialties = specialty_mapping.get(bid_category, [])
            related_matches = contractor_specialties.intersection(set(related_specialties))
            
            if related_matches:
                related_score = max(related_score, 0.7)  # 70% for related match
                reasons.append(f"Related specialty: {', '.join(related_matches)}")

        # General contractor fallback
        if 'general' in contractor_specialties:
            if related_score == 0.0:
                related_score = 0.5  # 50% for general contractor
                reasons.append("General contractor can handle this work type")

        return related_score, reasons

    async def _calculate_location_score(
        self,
        contractor: Dict[str, Any],
        bid_card: Dict[str, Any]
    ) -> tuple[float, bool]:
        """Calculate location proximity score and eligibility"""
        
        property_location = bid_card.get('property_location')
        if not property_location or not property_location.get('zip_code'):
            return 0.0, False

        property_zip = property_location['zip_code']
        
        # Get contractor service areas
        service_areas = await self.db.get_contractor_service_areas(contractor['id'])
        
        if not service_areas:
            return 0.0, False

        max_score = 0.0
        serves_location = False

        for area in service_areas:
            area_score, area_eligible = await self._score_service_area(
                area, property_location
            )
            
            if area_eligible:
                serves_location = True
                max_score = max(max_score, area_score)

        return max_score, serves_location

    async def _score_service_area(
        self,
        service_area: Dict[str, Any],
        property_location: Dict[str, Any]
    ) -> tuple[float, bool]:
        """Score a specific service area against property location"""
        
        area_type = service_area['area_type']
        property_zip = property_location['zip_code']

        # ZIP code based service area
        if area_type == 'zip_codes':
            zip_codes = service_area.get('zip_codes', [])
            if property_zip in zip_codes:
                return 1.0, True  # Perfect match for ZIP code
            return 0.0, False

        # Radius based service area
        elif area_type == 'radius':
            center_address = service_area.get('center_address')
            radius_miles = service_area.get('radius_miles', 0)
            
            if not center_address or not center_address.get('coordinates'):
                return 0.0, False

            # Calculate distance
            property_coords = property_location.get('coordinates')
            if not property_coords:
                # Geocode property if needed
                property_coords = await self._geocode_location(property_location)

            if property_coords:
                distance = geodesic(
                    center_address['coordinates'],
                    property_coords
                ).miles

                if distance <= radius_miles:
                    # Score based on proximity (closer = higher score)
                    score = max(0.1, 1.0 - (distance / radius_miles) * 0.8)
                    return score, True

            return 0.0, False

        # Cities/counties based service area
        elif area_type == 'cities_counties':
            property_city = property_location.get('city', '').lower()
            property_county = property_location.get('county', '').lower()
            
            served_cities = [city.lower() for city in service_area.get('cities', [])]
            served_counties = [county.lower() for county in service_area.get('counties', [])]

            if property_city in served_cities:
                return 1.0, True
            elif property_county in served_counties:
                return 0.8, True  # Slightly lower for county match

            return 0.0, False

        return 0.0, False

    async def _calculate_availability_score(
        self,
        contractor: Dict[str, Any],
        bid_card: Dict[str, Any]
    ) -> tuple[float, bool]:
        """Calculate availability score based on timeline and capacity"""
        
        # Check basic availability status
        if contractor.get('availability') != 'available':
            return 0.0, False

        # Get contractor availability details
        availability = await self.db.get_contractor_availability(contractor['id'])
        if not availability:
            return 0.5, True  # Default score if no detailed availability

        # Check job capacity
        max_jobs = availability.get('max_jobs_per_week', 10)
        current_jobs = availability.get('current_job_count', 0)
        
        capacity_ratio = 1.0 - (current_jobs / max_jobs)
        if capacity_ratio <= 0:
            return 0.0, False  # At capacity

        # Check timeline requirements
        project_timeline = bid_card.get('timeline')
        if project_timeline:
            urgency_score = await self._calculate_timeline_score(
                availability, project_timeline
            )
            return min(capacity_ratio, urgency_score), True

        return capacity_ratio, True

    async def _calculate_experience_score(
        self,
        contractor: Dict[str, Any],
        bid_card: Dict[str, Any]
    ) -> float:
        """Calculate experience and rating based score"""
        
        rating = contractor.get('rating', 0.0)
        total_projects = contractor.get('total_projects', 0)
        
        # Rating component (0-5 scale normalized to 0-1)
        rating_score = rating / 5.0 if rating > 0 else 0.3  # Default for new contractors
        
        # Experience component (logarithmic scale)
        if total_projects == 0:
            experience_score = 0.2  # New contractor baseline
        elif total_projects < 10:
            experience_score = 0.5
        elif total_projects < 50:
            experience_score = 0.7
        elif total_projects < 100:
            experience_score = 0.9
        else:
            experience_score = 1.0

        # Weighted combination
        return (rating_score * 0.7) + (experience_score * 0.3)

    async def _calculate_job_size_score(
        self,
        contractor: Dict[str, Any],
        bid_card: Dict[str, Any]
    ) -> tuple[float, bool]:
        """Calculate job size preference matching"""
        
        # Get job preferences
        preferences = await self.db.get_contractor_job_preferences(contractor['id'])
        if not preferences:
            # Use contractor table minimums as fallback
            min_size = contractor.get('min_project_size', 1000)
            max_size = contractor.get('max_project_size', 100000)
        else:
            min_size = preferences.get('minimum_job_size_dollars', 1000)
            max_size = preferences.get('maximum_job_size_dollars')

        # Get bid card budget
        project_budget = bid_card.get('budget_range')
        if not project_budget:
            return 0.7, True  # Default score if no budget specified

        # Parse budget range
        budget_min, budget_max = self._parse_budget_range(project_budget)
        
        # Check if job is within contractor preferences
        if budget_max < min_size:
            return 0.0, False  # Too small
        
        if max_size and budget_min > max_size:
            return 0.0, False  # Too large

        # Calculate preference score
        if min_size <= budget_min <= budget_max <= (max_size or float('inf')):
            return 1.0, True  # Perfect fit
        
        # Partial overlap scoring
        overlap_score = self._calculate_budget_overlap(
            (budget_min, budget_max),
            (min_size, max_size or 1000000)
        )
        
        return overlap_score, overlap_score > 0.3

    def _is_eligible(self, match_score: MatchScore) -> bool:
        """Check if contractor meets all eligibility requirements"""
        required_checks = [
            'location_served',
            'availability',
            'job_size_acceptable'
        ]
        
        return all(
            match_score.eligibility_checks.get(check, False)
            for check in required_checks
        )

    async def update_contractor_performance_metrics(
        self,
        contractor_id: str
    ) -> None:
        """Update contractor performance metrics for better matching"""
        try:
            # Calculate metrics from bid history
            metrics = await self._calculate_performance_metrics(contractor_id)
            
            # Update database
            await self.db.update_contractor_performance_metrics(
                contractor_id=contractor_id,
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Performance metrics update failed for {contractor_id}: {e}")
```

---

## Implementation Order

### Overview

This section outlines the step-by-step implementation sequence, ensuring each phase builds upon the previous while maintaining system stability and allowing for iterative testing.

### Phase 1: Database Foundation (Week 1-2)

#### Priority: Critical
**Goal**: Establish the database schema and core data structures

#### Tasks:
1. **Database Schema Creation**
   ```sql
   -- Execute database migrations in order:
   -- 1. Extend contractors table
   -- 2. Create credential tables
   -- 3. Create service area tables
   -- 4. Create availability tables
   -- 5. Create portfolio tables
   -- 6. Create job preferences tables
   -- 7. Create performance metrics tables
   -- 8. Create verification queue tables
   ```

2. **Database Functions and Triggers**
   - Implement profile completion calculation function
   - Create automatic triggers for profile updates
   - Set up credential expiry monitoring
   - Create performance metrics calculation procedures

3. **Data Migration Scripts**
   - Migrate existing contractor data to new schema
   - Preserve existing bid card relationships
   - Update existing API endpoints to handle new fields

#### Validation Criteria:
- [ ] All new tables created successfully
- [ ] Existing contractor data migrated without loss
- [ ] Profile completion calculation working
- [ ] Database performance tests pass

### Phase 2: Core API Development (Week 2-4)

#### Priority: Critical
**Goal**: Build the foundational API endpoints for contractor management

#### Tasks:
1. **Authentication & Authorization**
   ```python
   # Implement contractor authentication
   - extend existing JWT system for contractor roles
   - create role-based access control
   - implement contractor profile access controls
   ```

2. **Registration API**
   - Build contractor registration endpoint
   - Implement basic profile creation
   - Add email verification workflow
   - Create temporary password system

3. **Profile Management APIs**
   - CRUD operations for contractor profiles
   - Service area management endpoints
   - Availability management endpoints
   - Job preferences endpoints

4. **File Upload System**
   - Secure credential document upload
   - File validation and virus scanning
   - Storage organization by contractor and type
   - Document access controls

#### Validation Criteria:
- [ ] Registration flow creates complete contractor record
- [ ] All profile management endpoints functional
- [ ] File upload system handles all required document types
- [ ] API security tests pass

### Phase 3: Verification System (Week 4-6)

#### Priority: High
**Goal**: Implement automated and manual verification workflows

#### Tasks:
1. **Automated Verification Service**
   ```python
   # Implement verification APIs
   - License verification integration
   - Insurance carrier validation
   - Business entity verification
   - Phone and email verification
   ```

2. **Manual Review Queue**
   - Admin review interface
   - Queue management system
   - Assignment and escalation logic
   - Review workflow tracking

3. **Notification System**
   - Verification status notifications
   - Credential expiry alerts
   - Review assignment notifications
   - Status change communications

#### Validation Criteria:
- [ ] Automated verification detects valid credentials
- [ ] Manual review queue processes items efficiently
- [ ] Notification system sends appropriate alerts
- [ ] Verification workflow completes end-to-end

### Phase 4: Enhanced Matching Algorithm (Week 6-8)

#### Priority: High
**Goal**: Upgrade the contractor matching system with new profile data

#### Tasks:
1. **Matching Service Enhancement**
   ```python
   # Upgrade existing CDA system
   - Integrate new profile fields into scoring
   - Implement geographic matching improvements
   - Add availability-based filtering
   - Create preference-based scoring
   ```

2. **Performance Optimization**
   - Database query optimization
   - Caching layer implementation
   - Parallel scoring algorithms
   - Response time optimization

3. **Testing and Validation**
   - A/B testing framework
   - Match quality metrics
   - Performance benchmarking
   - Accuracy validation

#### Validation Criteria:
- [ ] New matching algorithm shows improved relevance
- [ ] Response times meet performance targets (<2 seconds)
- [ ] Match quality metrics improve over baseline
- [ ] System handles peak load requirements

### Phase 5: Frontend Onboarding Wizard (Week 8-10)

#### Priority: High
**Goal**: Create the contractor onboarding experience

#### Tasks:
1. **Multi-Step Wizard Implementation**
   ```typescript
   // Component development order:
   - OnboardingWizard shell
   - BasicInfoStep
   - BusinessDetailsStep  
   - CredentialsUploadStep
   - TradeSpecialtiesStep
   - ServiceAreasStep
   - AvailabilityStep
   - JobPreferencesStep
   - ProfileSetupStep
   ```

2. **Form Validation and UX**
   - Real-time validation
   - Progress tracking
   - Save and resume functionality
   - Mobile-responsive design

3. **Integration Testing**
   - End-to-end onboarding flow
   - File upload workflows
   - Error handling and recovery
   - Cross-browser compatibility

#### Validation Criteria:
- [ ] Complete onboarding flow works end-to-end
- [ ] Form validation prevents invalid data
- [ ] Mobile experience is fully functional
- [ ] Error handling provides clear guidance

### Phase 6: Dashboard and Profile Management (Week 10-12)

#### Priority: Medium
**Goal**: Build contractor dashboard and profile management interfaces

#### Tasks:
1. **Contractor Dashboard**
   ```typescript
   // Dashboard components:
   - Main dashboard overview
   - Job invitations display
   - Performance metrics view
   - Quick actions panel
   ```

2. **Profile Management Interface**
   - Profile editing capabilities
   - Credential management
   - Service area visualization
   - Portfolio management

3. **Performance Analytics**
   - Response rate tracking
   - Job completion metrics
   - Revenue analytics
   - Rating and review display

#### Validation Criteria:
- [ ] Dashboard provides comprehensive overview
- [ ] Profile editing maintains data integrity
- [ ] Performance metrics display accurately
- [ ] User experience is intuitive and efficient

### Phase 7: Admin Verification Interface (Week 12-14)

#### Priority: Medium
**Goal**: Create admin tools for contractor verification

#### Tasks:
1. **Admin Dashboard Enhancement**
   ```typescript
   // Admin verification components:
   - Verification queue interface
   - Contractor review panel
   - Document viewer
   - Approval/rejection workflow
   ```

2. **Workflow Management**
   - Review assignment system
   - Escalation handling
   - Batch processing tools
   - Performance tracking

3. **Reporting and Analytics**
   - Verification metrics
   - Queue performance analytics
   - Admin productivity tracking
   - Quality assurance reports

#### Validation Criteria:
- [ ] Admin can efficiently process verification queue
- [ ] Review workflow maintains audit trail
- [ ] Reporting provides actionable insights
- [ ] Queue performance meets SLA targets

### Phase 8: Mobile Optimization (Week 14-16)

#### Priority: Low
**Goal**: Optimize for mobile contractor experience

#### Tasks:
1. **Mobile-First Components**
   ```typescript
   // Mobile-specific implementations:
   - Touch-optimized interfaces
   - Offline capability
   - Push notifications
   - Location services
   ```

2. **Progressive Web App Features**
   - Offline job viewing
   - Background sync
   - Push notification support
   - App-like experience

3. **Performance Optimization**
   - Bundle size optimization
   - Lazy loading implementation
   - Caching strategies
   - Battery usage optimization

#### Validation Criteria:
- [ ] Mobile experience matches desktop functionality
- [ ] Offline capabilities work reliably
- [ ] Performance meets mobile standards
- [ ] Push notifications deliver effectively

### Phase 9: Integration Testing and Quality Assurance (Week 16-18)

#### Priority: Critical
**Goal**: Comprehensive system testing and validation

#### Tasks:
1. **End-to-End Testing**
   ```python
   # Test scenarios:
   - Complete contractor onboarding
   - Verification workflow
   - Job matching accuracy
   - Profile management
   - Admin workflows
   ```

2. **Performance Testing**
   - Load testing with realistic data volumes
   - Stress testing for peak usage
   - Database performance validation
   - API response time verification

3. **Security Testing**
   - Authentication and authorization
   - File upload security
   - Data privacy compliance
   - Input validation testing

#### Validation Criteria:
- [ ] All end-to-end scenarios pass
- [ ] Performance meets all SLA requirements
- [ ] Security vulnerabilities addressed
- [ ] Data integrity maintained under all conditions

### Phase 10: Deployment and Monitoring (Week 18-20)

#### Priority: Critical
**Goal**: Deploy system and establish monitoring

#### Tasks:
1. **Production Deployment**
   ```bash
   # Deployment sequence:
   - Database migrations
   - API deployment
   - Frontend deployment
   - Configuration updates
   - DNS updates
   ```

2. **Monitoring and Alerting**
   - Application performance monitoring
   - Database performance tracking
   - Error rate monitoring
   - User experience analytics

3. **Documentation and Training**
   - Admin user training
   - API documentation
   - Troubleshooting guides
   - Monitoring playbooks

#### Validation Criteria:
- [ ] All systems deployed successfully
- [ ] Monitoring captures all critical metrics
- [ ] Documentation is complete and accurate
- [ ] Support team trained on new features

---

## Integration with Existing Systems

### Bid Card System Integration

The contractor onboarding system integrates seamlessly with the existing bid card ecosystem:

```python
# Integration points:
- Contractor matching for bid cards uses new profile data
- Service area validation ensures accurate geographic matching  
- Availability checking prevents overloaded contractors
- Performance metrics influence contractor ranking
- Job preferences filter inappropriate matches
```

### Authentication System Extension

Extends the current user authentication to support contractor roles:

```python
# auth/roles.py
CONTRACTOR_PERMISSIONS = [
    'view_own_profile',
    'edit_own_profile', 
    'upload_credentials',
    'manage_availability',
    'view_job_invitations',
    'submit_bids',
    'manage_portfolio'
]
```

### Unified Memory System Compatibility

Integrates with the existing unified conversation system for contractor interactions:

```sql
-- Contractor conversations use existing unified_conversations tables
-- with contractor_id as entity_id and 'contractor' as entity_type
```

This comprehensive technical implementation plan provides a structured approach to building the contractor onboarding feature while maintaining compatibility with existing InstaBids systems and ensuring scalable, secure, and user-friendly contractor management capabilities.