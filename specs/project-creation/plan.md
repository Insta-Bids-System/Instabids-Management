# Project Creation Technical Implementation Plan

## Executive Summary

This document outlines the technical implementation plan for the InstaBids project creation feature, designed to enable property managers to create maintenance projects in under 2 minutes with automatic contractor matching and invitation.

## 1. Database Design

### 1.1 Core Tables Schema

#### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    property_manager_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL CHECK (length(description) <= 2000),
    category project_category NOT NULL,
    urgency_level urgency_type NOT NULL,
    bid_deadline TIMESTAMP NOT NULL,
    preferred_start_date DATE,
    completion_deadline DATE,
    budget_range budget_range_type,
    payment_terms TEXT,
    requires_insurance BOOLEAN DEFAULT false,
    requires_license BOOLEAN DEFAULT false,
    minimum_bids_required INTEGER DEFAULT 3,
    is_invitation_only BOOLEAN DEFAULT false,
    status project_status DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    qr_code_url TEXT,
    
    -- Access Instructions
    gate_code VARCHAR(50),
    lockbox_code VARCHAR(50),
    key_location TEXT,
    access_contact VARCHAR(100),
    pets_on_property BOOLEAN DEFAULT false,
    hazards_notes TEXT,
    parking_instructions TEXT,
    work_hour_restrictions TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    draft_expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days'),
    
    -- Constraints
    CONSTRAINT valid_bid_deadline CHECK (bid_deadline > NOW()),
    CONSTRAINT valid_start_date CHECK (preferred_start_date >= CURRENT_DATE),
    CONSTRAINT valid_completion CHECK (completion_deadline IS NULL OR completion_deadline > preferred_start_date)
);

-- Enum types
CREATE TYPE project_category AS ENUM (
    'plumbing', 'electrical', 'hvac', 'roofing', 'painting', 
    'landscaping', 'general_maintenance', 'other'
);

CREATE TYPE urgency_type AS ENUM (
    'emergency', 'urgent', 'routine', 'scheduled'
);

CREATE TYPE budget_range_type AS ENUM (
    'under_500', '500_1000', '1000_5000', '5000_10000', 'over_10000', 'open_to_quotes'
);

CREATE TYPE project_status AS ENUM (
    'draft', 'open_for_bids', 'bidding_closed', 'awarded', 'in_progress', 'completed', 'archived'
);
```

#### Project Media Table
```sql
CREATE TABLE project_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_type media_type NOT NULL,
    file_size INTEGER NOT NULL,
    caption TEXT,
    display_order INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    upload_status upload_status_type DEFAULT 'uploading',
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_primary_per_project UNIQUE (project_id, is_primary) WHERE is_primary = true,
    CONSTRAINT valid_file_size_photo CHECK (
        (file_type = 'photo' AND file_size <= 10485760) OR  -- 10MB for photos
        (file_type = 'video' AND file_size <= 104857600)    -- 100MB for videos
    )
);

CREATE TYPE media_type AS ENUM ('photo', 'video');
CREATE TYPE upload_status_type AS ENUM ('uploading', 'completed', 'failed');
```

#### Project Invitations Table
```sql
CREATE TABLE project_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID NOT NULL REFERENCES contractors(id),
    invitation_wave INTEGER NOT NULL DEFAULT 1,
    invited_at TIMESTAMP DEFAULT NOW(),
    notification_sent_at TIMESTAMP,
    viewed_at TIMESTAMP,
    responded_at TIMESTAMP,
    response_type invitation_response,
    
    UNIQUE(project_id, contractor_id)
);

CREATE TYPE invitation_response AS ENUM ('accepted', 'declined', 'ignored');
```

#### Project Questions Table
```sql
CREATE TABLE project_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID NOT NULL REFERENCES contractors(id),
    question TEXT NOT NULL,
    answer TEXT,
    asked_at TIMESTAMP DEFAULT NOW(),
    answered_at TIMESTAMP,
    is_public BOOLEAN DEFAULT true
);
```

#### Project Templates Table (Future Enhancement)
```sql
CREATE TABLE project_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_manager_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    category project_category NOT NULL,
    template_data JSONB NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 1.2 Indexes for Performance

```sql
-- Core lookup indexes
CREATE INDEX idx_projects_property_manager ON projects(property_manager_id);
CREATE INDEX idx_projects_property ON projects(property_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_category ON projects(category);
CREATE INDEX idx_projects_published_at ON projects(published_at DESC) WHERE published_at IS NOT NULL;

-- Contractor matching indexes
CREATE INDEX idx_projects_category_urgency ON projects(category, urgency_level) WHERE status = 'open_for_bids';
CREATE INDEX idx_projects_bid_deadline ON projects(bid_deadline) WHERE status = 'open_for_bids';

-- Media management
CREATE INDEX idx_project_media_project ON project_media(project_id, display_order);
CREATE INDEX idx_project_media_primary ON project_media(project_id) WHERE is_primary = true;

-- Invitation tracking
CREATE INDEX idx_project_invitations_contractor ON project_invitations(contractor_id, invited_at DESC);
CREATE INDEX idx_project_invitations_project_wave ON project_invitations(project_id, invitation_wave);

-- Questions
CREATE INDEX idx_project_questions_project ON project_questions(project_id, asked_at DESC);
CREATE INDEX idx_project_questions_contractor ON project_questions(contractor_id, asked_at DESC);
```

### 1.3 Migration File

```sql
-- Migration: 001_create_project_creation_system.sql
BEGIN;

-- Create enum types
CREATE TYPE project_category AS ENUM (
    'plumbing', 'electrical', 'hvac', 'roofing', 'painting', 
    'landscaping', 'general_maintenance', 'other'
);

CREATE TYPE urgency_type AS ENUM (
    'emergency', 'urgent', 'routine', 'scheduled'
);

CREATE TYPE budget_range_type AS ENUM (
    'under_500', '500_1000', '1000_5000', '5000_10000', 'over_10000', 'open_to_quotes'
);

CREATE TYPE project_status AS ENUM (
    'draft', 'open_for_bids', 'bidding_closed', 'awarded', 'in_progress', 'completed', 'archived'
);

CREATE TYPE media_type AS ENUM ('photo', 'video');
CREATE TYPE upload_status_type AS ENUM ('uploading', 'completed', 'failed');
CREATE TYPE invitation_response AS ENUM ('accepted', 'declined', 'ignored');

-- Create main projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id UUID NOT NULL REFERENCES properties(id),
    property_manager_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL CHECK (length(description) <= 2000),
    category project_category NOT NULL,
    urgency_level urgency_type NOT NULL,
    bid_deadline TIMESTAMP NOT NULL,
    preferred_start_date DATE,
    completion_deadline DATE,
    budget_range budget_range_type,
    payment_terms TEXT,
    requires_insurance BOOLEAN DEFAULT false,
    requires_license BOOLEAN DEFAULT false,
    minimum_bids_required INTEGER DEFAULT 3,
    is_invitation_only BOOLEAN DEFAULT false,
    status project_status DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    qr_code_url TEXT,
    
    -- Access Instructions
    gate_code VARCHAR(50),
    lockbox_code VARCHAR(50),
    key_location TEXT,
    access_contact VARCHAR(100),
    pets_on_property BOOLEAN DEFAULT false,
    hazards_notes TEXT,
    parking_instructions TEXT,
    work_hour_restrictions TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    draft_expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '7 days'),
    
    -- Constraints
    CONSTRAINT valid_bid_deadline CHECK (bid_deadline > NOW()),
    CONSTRAINT valid_start_date CHECK (preferred_start_date >= CURRENT_DATE),
    CONSTRAINT valid_completion CHECK (completion_deadline IS NULL OR completion_deadline > preferred_start_date)
);

-- Create media table
CREATE TABLE project_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_type media_type NOT NULL,
    file_size INTEGER NOT NULL,
    caption TEXT,
    display_order INTEGER NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    upload_status upload_status_type DEFAULT 'uploading',
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT unique_primary_per_project UNIQUE (project_id, is_primary) WHERE is_primary = true,
    CONSTRAINT valid_file_size_photo CHECK (
        (file_type = 'photo' AND file_size <= 10485760) OR
        (file_type = 'video' AND file_size <= 104857600)
    )
);

-- Create invitations table
CREATE TABLE project_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID NOT NULL REFERENCES contractors(id),
    invitation_wave INTEGER NOT NULL DEFAULT 1,
    invited_at TIMESTAMP DEFAULT NOW(),
    notification_sent_at TIMESTAMP,
    viewed_at TIMESTAMP,
    responded_at TIMESTAMP,
    response_type invitation_response,
    
    UNIQUE(project_id, contractor_id)
);

-- Create questions table
CREATE TABLE project_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID NOT NULL REFERENCES contractors(id),
    question TEXT NOT NULL,
    answer TEXT,
    asked_at TIMESTAMP DEFAULT NOW(),
    answered_at TIMESTAMP,
    is_public BOOLEAN DEFAULT true
);

-- Create templates table
CREATE TABLE project_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_manager_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    category project_category NOT NULL,
    template_data JSONB NOT NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_projects_property_manager ON projects(property_manager_id);
CREATE INDEX idx_projects_property ON projects(property_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_category ON projects(category);
CREATE INDEX idx_projects_published_at ON projects(published_at DESC) WHERE published_at IS NOT NULL;
CREATE INDEX idx_projects_category_urgency ON projects(category, urgency_level) WHERE status = 'open_for_bids';
CREATE INDEX idx_projects_bid_deadline ON projects(bid_deadline) WHERE status = 'open_for_bids';

CREATE INDEX idx_project_media_project ON project_media(project_id, display_order);
CREATE INDEX idx_project_media_primary ON project_media(project_id) WHERE is_primary = true;

CREATE INDEX idx_project_invitations_contractor ON project_invitations(contractor_id, invited_at DESC);
CREATE INDEX idx_project_invitations_project_wave ON project_invitations(project_id, invitation_wave);

CREATE INDEX idx_project_questions_project ON project_questions(project_id, asked_at DESC);
CREATE INDEX idx_project_questions_contractor ON project_questions(contractor_id, asked_at DESC);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
```

## 2. API Design

### 2.1 Core Endpoints

#### Project Creation API
```typescript
// POST /api/projects
interface CreateProjectRequest {
  property_id: string;
  title: string;
  description: string;
  category: ProjectCategory;
  urgency_level: UrgencyType;
  bid_deadline: string; // ISO timestamp
  preferred_start_date?: string; // ISO date
  completion_deadline?: string; // ISO date
  budget_range?: BudgetRangeType;
  payment_terms?: string;
  requires_insurance?: boolean;
  requires_license?: boolean;
  minimum_bids_required?: number;
  is_invitation_only?: boolean;
  
  // Access instructions
  gate_code?: string;
  lockbox_code?: string;
  key_location?: string;
  access_contact?: string;
  pets_on_property?: boolean;
  hazards_notes?: string;
  parking_instructions?: string;
  work_hour_restrictions?: string;
}

interface CreateProjectResponse {
  id: string;
  status: 'draft' | 'published';
  qr_code_url?: string;
  upload_urls?: MediaUploadUrl[];
}
```

#### Media Upload API
```typescript
// POST /api/projects/{id}/media/upload-url
interface MediaUploadRequest {
  file_type: 'photo' | 'video';
  file_size: number;
  file_name: string;
  caption?: string;
  display_order: number;
  is_primary?: boolean;
}

interface MediaUploadResponse {
  upload_url: string;
  media_id: string;
  expires_at: string;
}

// PUT /api/projects/{id}/media/{media_id}/complete
interface CompleteUploadRequest {
  file_path: string;
  actual_file_size: number;
}
```

#### Project Management API
```typescript
// GET /api/projects/{id}
interface GetProjectResponse {
  id: string;
  property: PropertySummary;
  title: string;
  description: string;
  category: ProjectCategory;
  urgency_level: UrgencyType;
  bid_deadline: string;
  preferred_start_date?: string;
  completion_deadline?: string;
  budget_range?: BudgetRangeType;
  requires_insurance: boolean;
  requires_license: boolean;
  status: ProjectStatus;
  view_count: number;
  bid_count: number;
  question_count: number;
  media: ProjectMedia[];
  access_instructions: AccessInstructions;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

// PUT /api/projects/{id}
// PATCH /api/projects/{id}/status
// DELETE /api/projects/{id}

// GET /api/projects
interface ListProjectsRequest {
  property_id?: string;
  status?: ProjectStatus[];
  category?: ProjectCategory[];
  page?: number;
  limit?: number;
  sort_by?: 'created_at' | 'updated_at' | 'bid_deadline';
  sort_order?: 'asc' | 'desc';
}
```

#### Contractor Matching API
```typescript
// POST /api/projects/{id}/match-contractors
interface MatchContractorsRequest {
  max_contractors?: number;
  include_specific_ids?: string[];
  exclude_contractor_ids?: string[];
}

interface MatchContractorsResponse {
  matched_contractors: ContractorMatch[];
  total_matches: number;
  invitation_strategy: InvitationStrategy;
}

interface ContractorMatch {
  contractor_id: string;
  contractor_name: string;
  rating: number;
  response_rate: number;
  completion_rate: number;
  price_competitiveness: number;
  match_score: number;
  distance_miles: number;
  availability_status: string;
}

// POST /api/projects/{id}/invite-contractors
interface InviteContractorsRequest {
  contractor_ids: string[];
  invitation_wave?: number;
  custom_message?: string;
}
```

#### Project Questions API
```typescript
// GET /api/projects/{id}/questions
// POST /api/projects/{id}/questions
interface CreateQuestionRequest {
  question: string;
  is_public?: boolean;
}

// PUT /api/projects/{id}/questions/{question_id}/answer
interface AnswerQuestionRequest {
  answer: string;
}
```

### 2.2 Authentication & Authorization

```typescript
// All endpoints require authentication
// Property managers can only access their own projects
// Contractors can only view projects they're invited to

interface AuthMiddleware {
  requireAuth: boolean;
  requireRoles: ['property_manager'] | ['contractor'] | ['property_manager', 'contractor'];
  resourceOwnership?: {
    resource: 'project' | 'property';
    id_param: string;
    ownership_field: string;
  };
}

// Example endpoint definitions
const endpoints = {
  'POST /api/projects': {
    auth: { requireAuth: true, requireRoles: ['property_manager'] }
  },
  'GET /api/projects/{id}': {
    auth: { 
      requireAuth: true, 
      requireRoles: ['property_manager', 'contractor'],
      resourceOwnership: {
        resource: 'project',
        id_param: 'id',
        ownership_field: 'property_manager_id'
      }
    }
  }
};
```

### 2.3 Error Handling Schema

```typescript
interface APIError {
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
    field_errors?: Record<string, string[]>;
  };
  request_id: string;
  timestamp: string;
}

// Standard error codes
const ErrorCodes = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  UPLOAD_FAILED: 'UPLOAD_FAILED',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  PROJECT_CREATION_LIMIT: 'PROJECT_CREATION_LIMIT',
  CONTRACTOR_MATCHING_FAILED: 'CONTRACTOR_MATCHING_FAILED'
} as const;
```

## 3. Frontend Components Architecture

### 3.1 Component Hierarchy

```
ProjectCreationWizard
├── WizardNavigation
├── WizardSteps
│   ├── PropertySelectionStep
│   │   ├── PropertyDropdown
│   │   ├── PropertyDetails
│   │   └── AccessInstructions
│   ├── IssueDescriptionStep
│   │   ├── TitleInput
│   │   ├── DescriptionTextarea
│   │   ├── CategorySelector
│   │   └── VoiceRecorder (mobile)
│   ├── TimelineStep
│   │   ├── UrgencySelector
│   │   ├── BidDeadlineSelector
│   │   ├── DatePicker
│   │   └── TimelinePreview
│   ├── MediaUploadStep
│   │   ├── MediaUploader
│   │   ├── MediaGrid
│   │   ├── MediaItem
│   │   ├── CameraCapture (mobile)
│   │   └── MediaReorder
│   ├── PreferencesStep
│   │   ├── BudgetRangeSelector
│   │   ├── RequirementsToggles
│   │   └── PaymentTermsInput
│   └── ReviewStep
│       ├── ProjectSummary
│       ├── ContractorPreview
│       └── PublishActions
├── DraftManager
├── ProgressIndicator
└── MobileOptimizations
    ├── SwipeNavigation
    ├── CameraFirst
    └── OneThumbNavigation
```

### 3.2 State Management Strategy

#### Global State (Redux/Zustand)
```typescript
interface ProjectCreationState {
  // Current wizard state
  currentStep: number;
  isLoading: boolean;
  errors: Record<string, string[]>;
  
  // Form data
  projectData: Partial<CreateProjectRequest>;
  mediaItems: MediaItem[];
  uploadProgress: Record<string, number>;
  
  // Supporting data
  properties: Property[];
  matchedContractors: ContractorMatch[];
  
  // Draft management
  draftId?: string;
  lastSaved: string;
  hasUnsavedChanges: boolean;
}

interface MediaItem {
  id: string;
  file: File;
  preview_url: string;
  upload_url?: string;
  upload_status: 'pending' | 'uploading' | 'completed' | 'failed';
  upload_progress: number;
  caption?: string;
  display_order: number;
  is_primary: boolean;
}

// Actions
const actions = {
  // Navigation
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  previousStep: () => void;
  
  // Form data
  updateProjectData: (data: Partial<CreateProjectRequest>) => void;
  addMediaItem: (item: MediaItem) => void;
  removeMediaItem: (id: string) => void;
  reorderMedia: (items: MediaItem[]) => void;
  setPrimaryMedia: (id: string) => void;
  
  // API operations
  saveDraft: () => Promise<void>;
  loadDraft: (id: string) => Promise<void>;
  publishProject: () => Promise<string>;
  uploadMedia: (item: MediaItem) => Promise<void>;
  
  // Contractor matching
  matchContractors: () => Promise<void>;
  inviteContractors: (contractorIds: string[]) => Promise<void>;
};
```

#### Component-Level State
```typescript
// Individual components manage their own UI state
interface ComponentState {
  // Form validation
  fieldErrors: Record<string, string>;
  fieldTouched: Record<string, boolean>;
  
  // UI interactions
  isExpanded: boolean;
  showTooltip: boolean;
  dragActive: boolean;
  
  // Temporary data
  searchQuery: string;
  filteredOptions: any[];
}
```

### 3.3 Form Validation Strategy

```typescript
// Validation schema using Zod
import { z } from 'zod';

const ProjectValidationSchema = z.object({
  property_id: z.string().uuid('Invalid property'),
  title: z.string()
    .min(1, 'Title is required')
    .max(100, 'Title too long'),
  description: z.string()
    .min(10, 'Description too short')
    .max(2000, 'Description too long'),
  category: z.enum(['plumbing', 'electrical', /* ... */]),
  urgency_level: z.enum(['emergency', 'urgent', 'routine', 'scheduled']),
  bid_deadline: z.string().datetime().refine(
    (date) => new Date(date) > new Date(),
    'Bid deadline must be in the future'
  ),
  preferred_start_date: z.string().date().optional().refine(
    (date) => !date || new Date(date) >= new Date(),
    'Start date cannot be in the past'
  ),
  // ... other fields
});

// Step-specific validation
const StepValidations = {
  1: ProjectValidationSchema.pick({ property_id: true }),
  2: ProjectValidationSchema.pick({ 
    title: true, 
    description: true, 
    category: true 
  }),
  3: ProjectValidationSchema.pick({ 
    urgency_level: true, 
    bid_deadline: true, 
    preferred_start_date: true 
  }),
  4: z.object({
    media_items: z.array(z.any()).min(1, 'At least one photo required')
  }),
  5: z.object({}), // Optional step
  6: ProjectValidationSchema // Full validation
};
```

### 3.4 Mobile Responsiveness Strategy

```scss
// Mobile-first responsive design
.project-wizard {
  // Base mobile styles
  padding: 1rem;
  
  @media (min-width: 768px) {
    // Tablet styles
    padding: 2rem;
    max-width: 768px;
    margin: 0 auto;
  }
  
  @media (min-width: 1024px) {
    // Desktop styles
    max-width: 1024px;
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 2rem;
  }
}

// Touch-friendly interactions
.wizard-button {
  min-height: 44px; // iOS recommendation
  padding: 12px 24px;
  font-size: 16px; // Prevents zoom on iOS
}

// Swipe navigation
.wizard-steps {
  display: flex;
  overflow-x: hidden;
  scroll-snap-type: x mandatory;
  
  .step {
    flex: 0 0 100%;
    scroll-snap-align: start;
  }
}
```

## 4. File Upload Strategy

### 4.1 Upload Flow Architecture

```typescript
// Multi-step upload process
interface UploadFlow {
  1: 'Client-side validation';
  2: 'Request upload URL from server';
  3: 'Direct upload to cloud storage';
  4: 'Notify server of completion';
  5: 'Update project media records';
}

// Upload service
class MediaUploadService {
  async uploadFile(
    projectId: string, 
    file: File, 
    metadata: MediaMetadata
  ): Promise<MediaItem> {
    // 1. Validate file
    this.validateFile(file);
    
    // 2. Request signed upload URL
    const uploadUrl = await this.getUploadUrl(projectId, {
      file_type: file.type.startsWith('image/') ? 'photo' : 'video',
      file_size: file.size,
      file_name: file.name,
      ...metadata
    });
    
    // 3. Upload directly to S3/Supabase Storage
    const uploadResult = await this.uploadToStorage(uploadUrl.upload_url, file);
    
    // 4. Complete upload on server
    const mediaItem = await this.completeUpload(uploadUrl.media_id, {
      file_path: uploadResult.file_path,
      actual_file_size: file.size
    });
    
    return mediaItem;
  }
  
  private validateFile(file: File): void {
    const MAX_PHOTO_SIZE = 10 * 1024 * 1024; // 10MB
    const MAX_VIDEO_SIZE = 100 * 1024 * 1024; // 100MB
    const MAX_VIDEO_DURATION = 120; // 2 minutes
    
    if (file.type.startsWith('image/')) {
      if (file.size > MAX_PHOTO_SIZE) {
        throw new Error('Photo size exceeds 10MB limit');
      }
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
        throw new Error('Invalid photo format');
      }
    } else if (file.type.startsWith('video/')) {
      if (file.size > MAX_VIDEO_SIZE) {
        throw new Error('Video size exceeds 100MB limit');
      }
      if (!['video/mp4', 'video/quicktime', 'video/x-msvideo'].includes(file.type)) {
        throw new Error('Invalid video format');
      }
    } else {
      throw new Error('Invalid file type');
    }
  }
}
```

### 4.2 Storage Configuration

```typescript
// Supabase Storage configuration
const storageConfig = {
  bucket: 'project-media',
  path_structure: 'projects/{project_id}/{media_id}.{extension}',
  policies: {
    upload: 'authenticated users can upload to their own projects',
    read: 'public read access with signed URLs',
    delete: 'project owners only'
  }
};

// File processing pipeline
interface ProcessingPipeline {
  photos: {
    resize: '1920x1080 max, maintain aspect ratio';
    compress: 'JPEG quality 85%, WebP where supported';
    thumbnails: ['150x150', '300x300', '600x400'];
    formats: 'Generate WebP versions for modern browsers';
  };
  videos: {
    compress: 'H.264, max bitrate 2Mbps';
    thumbnails: 'Extract frame at 2 seconds';
    formats: 'MP4 with web-optimized encoding';
  };
}
```

### 4.3 Client-Side Optimization

```typescript
// Image compression before upload
class ImageProcessor {
  async compressImage(file: File, maxSize: number = 1920): Promise<File> {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        // Calculate new dimensions
        const { width, height } = this.calculateDimensions(
          img.width, 
          img.height, 
          maxSize
        );
        
        // Resize on canvas
        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);
        
        // Convert to blob
        canvas.toBlob((blob) => {
          resolve(new File([blob], file.name, { type: 'image/jpeg' }));
        }, 'image/jpeg', 0.85);
      };
      
      img.src = URL.createObjectURL(file);
    });
  }
  
  private calculateDimensions(
    width: number, 
    height: number, 
    maxSize: number
  ): { width: number; height: number } {
    if (width <= maxSize && height <= maxSize) {
      return { width, height };
    }
    
    const ratio = Math.min(maxSize / width, maxSize / height);
    return {
      width: Math.round(width * ratio),
      height: Math.round(height * ratio)
    };
  }
}

// Progressive upload with retry
class UploadManager {
  private retryAttempts = 3;
  private chunkSize = 1024 * 1024; // 1MB chunks for large files
  
  async uploadWithProgress(
    file: File, 
    uploadUrl: string,
    onProgress: (progress: number) => void
  ): Promise<void> {
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        if (file.size > this.chunkSize * 5) {
          // Use chunked upload for large files
          await this.chunkedUpload(file, uploadUrl, onProgress);
        } else {
          // Direct upload for smaller files
          await this.directUpload(file, uploadUrl, onProgress);
        }
        return;
      } catch (error) {
        if (attempt === this.retryAttempts) throw error;
        await this.delay(attempt * 1000); // Exponential backoff
      }
    }
  }
}
```

### 4.4 Security Considerations

```typescript
// File validation and sanitization
const securityChecks = {
  fileType: {
    allowedMimeTypes: [
      'image/jpeg', 'image/png', 'image/webp',
      'video/mp4', 'video/quicktime', 'video/x-msvideo'
    ],
    magicNumberValidation: true, // Check file headers
    extensionWhitelist: ['.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.avi']
  },
  
  malwareScanning: {
    enabled: true,
    service: 'clamav', // Or cloud service like VirusTotal
    quarantineOnDetection: true
  },
  
  metadata: {
    stripExifData: true, // Remove location and camera info
    sanitizeFilenames: true, // Remove special characters
    maxFilenameLength: 255
  },
  
  rateLimiting: {
    maxUploadsPerMinute: 10,
    maxUploadsPerDay: 100,
    maxTotalSizePerDay: '1GB'
  }
};
```

## 5. AI Integration Points

### 5.1 SmartScope AI Integration

```typescript
// SmartScope service for automatic project categorization
class SmartScopeService {
  async analyzeProjectScope(
    description: string, 
    mediaUrls: string[]
  ): Promise<ScopeAnalysis> {
    const response = await fetch('/api/ai/analyze-scope', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description,
        media_urls: mediaUrls,
        analysis_type: 'project_creation'
      })
    });
    
    return response.json();
  }
}

interface ScopeAnalysis {
  suggested_category: ProjectCategory;
  confidence_score: number;
  estimated_timeline: {
    min_hours: number;
    max_hours: number;
  };
  suggested_budget_range: BudgetRangeType;
  complexity_score: number; // 1-10 scale
  required_trades: string[];
  potential_issues: string[];
  materials_needed: string[];
  urgency_indicators: string[];
}

// Integration points in project creation flow
const aiIntegrationPoints = {
  step2_description: {
    trigger: 'on_description_blur',
    action: 'suggest_category_and_details',
    debounce: 2000 // Wait 2s after typing stops
  },
  
  step4_media_upload: {
    trigger: 'on_media_processed',
    action: 'analyze_visual_scope',
    batch: true // Wait for all uploads to complete
  },
  
  step5_budget: {
    trigger: 'on_scope_analysis_complete',
    action: 'suggest_budget_range',
    autoFill: false // Suggest but don't auto-fill
  }
};
```

### 5.2 Contractor Matching Algorithm

```typescript
// Advanced contractor matching service
class ContractorMatchingService {
  async findMatchingContractors(
    project: CreateProjectRequest,
    scopeAnalysis?: ScopeAnalysis
  ): Promise<ContractorMatch[]> {
    const matchingCriteria = {
      // Primary filters
      trade_category: project.category,
      service_area: this.getServiceAreaFromProperty(project.property_id),
      availability: this.calculateAvailabilityWindow(project),
      credentials: this.getRequiredCredentials(project),
      
      // AI-enhanced criteria
      complexity_match: scopeAnalysis?.complexity_score,
      specialization_match: scopeAnalysis?.required_trades,
      
      // Performance criteria
      response_rate_threshold: 0.7, // 70% minimum
      completion_rate_threshold: 0.85, // 85% minimum
      rating_threshold: 4.0 // 4+ stars
    };
    
    return this.executeMatchingAlgorithm(matchingCriteria);
  }
  
  private async executeMatchingAlgorithm(
    criteria: MatchingCriteria
  ): Promise<ContractorMatch[]> {
    // Multi-stage filtering and scoring
    const contractors = await this.getEligibleContractors(criteria);
    
    return contractors.map(contractor => ({
      ...contractor,
      match_score: this.calculateMatchScore(contractor, criteria)
    })).sort((a, b) => b.match_score - a.match_score);
  }
  
  private calculateMatchScore(
    contractor: Contractor, 
    criteria: MatchingCriteria
  ): number {
    const weights = {
      category_match: 0.25,
      location_proximity: 0.20,
      availability: 0.15,
      response_rate: 0.15,
      rating: 0.15,
      completion_rate: 0.10
    };
    
    const scores = {
      category_match: this.getCategoryMatchScore(contractor, criteria),
      location_proximity: this.getLocationScore(contractor, criteria),
      availability: this.getAvailabilityScore(contractor, criteria),
      response_rate: contractor.response_rate,
      rating: contractor.rating / 5.0,
      completion_rate: contractor.completion_rate
    };
    
    return Object.entries(weights).reduce(
      (total, [key, weight]) => total + (scores[key] * weight),
      0
    );
  }
}
```

### 5.3 Intelligent Notification System

```typescript
// Smart notification dispatch based on urgency and contractor patterns
class IntelligentNotificationService {
  async dispatchProjectNotifications(
    projectId: string,
    matchedContractors: ContractorMatch[]
  ): Promise<void> {
    const project = await this.getProject(projectId);
    const strategy = this.determineNotificationStrategy(project);
    
    switch (strategy.type) {
      case 'immediate_broadcast':
        await this.sendImmediateNotifications(project, matchedContractors);
        break;
        
      case 'staggered_waves':
        await this.sendStaggeredNotifications(project, matchedContractors, strategy);
        break;
        
      case 'premium_first':
        await this.sendPremiumFirstNotifications(project, matchedContractors);
        break;
    }
  }
  
  private determineNotificationStrategy(project: Project): NotificationStrategy {
    if (project.urgency_level === 'emergency') {
      return {
        type: 'immediate_broadcast',
        max_contractors: 50,
        follow_up_hours: 1
      };
    }
    
    if (project.urgency_level === 'urgent') {
      return {
        type: 'staggered_waves',
        wave_size: 10,
        wave_interval_hours: 2,
        max_waves: 3
      };
    }
    
    return {
      type: 'premium_first',
      premium_wave_size: 5,
      general_wave_delay_hours: 4,
      general_wave_size: 15
    };
  }
  
  async sendPersonalizedNotification(
    contractor: ContractorMatch,
    project: Project
  ): Promise<void> {
    const notification = await this.generatePersonalizedMessage(contractor, project);
    
    // Multi-channel notification
    await Promise.all([
      this.sendSMSNotification(contractor.phone, notification.sms),
      this.sendEmailNotification(contractor.email, notification.email),
      this.sendInAppNotification(contractor.id, notification.inApp)
    ]);
  }
  
  private async generatePersonalizedMessage(
    contractor: ContractorMatch,
    project: Project
  ): Promise<PersonalizedNotification> {
    // AI-generated personalized messages based on:
    // - Contractor's past project types
    // - Response patterns
    // - Communication preferences
    // - Project urgency and details
    
    return {
      sms: `Hi ${contractor.name}! New ${project.category} project in ${project.location}. ${project.urgency_level} priority. Bid deadline: ${project.bid_deadline}. View details: ${project.link}`,
      email: this.generateEmailTemplate(contractor, project),
      inApp: this.generateInAppNotification(contractor, project)
    };
  }
}
```

## 6. Implementation Order & Dependencies

### 6.1 Phase 1: Core Infrastructure (Week 1-2)

#### Sprint 1.1: Database Foundation
- [ ] Create database migration scripts
- [ ] Set up enum types and constraints
- [ ] Create core tables (projects, project_media, project_invitations)
- [ ] Add indexes for performance
- [ ] Create database triggers and functions

**Dependencies**: Database access, migration system
**Testing**: Database schema validation, constraint testing

#### Sprint 1.2: Basic API Endpoints
- [ ] Project CRUD endpoints
- [ ] Media upload URL generation
- [ ] Basic authentication middleware
- [ ] Error handling framework
- [ ] API documentation setup

**Dependencies**: Database schema, authentication system
**Testing**: API endpoint testing, authentication testing

### 6.2 Phase 2: Media Upload System (Week 2-3)

#### Sprint 2.1: File Upload Infrastructure
- [ ] Supabase Storage configuration
- [ ] Signed URL generation service
- [ ] File validation service
- [ ] Upload completion tracking
- [ ] Error recovery mechanisms

**Dependencies**: Supabase Storage, core API
**Testing**: Upload flow testing, error handling

#### Sprint 2.2: Client-Side Upload Components
- [ ] Media upload component
- [ ] Progress tracking
- [ ] Image compression service
- [ ] Drag-and-drop interface
- [ ] Mobile camera integration

**Dependencies**: Upload API, React components
**Testing**: Cross-browser upload testing, mobile testing

### 6.3 Phase 3: Project Creation UI (Week 3-4)

#### Sprint 3.1: Wizard Framework
- [ ] Multi-step wizard component
- [ ] State management setup
- [ ] Navigation between steps
- [ ] Progress indicator
- [ ] Draft auto-save functionality

**Dependencies**: API endpoints, state management library
**Testing**: Wizard navigation, state persistence

#### Sprint 3.2: Form Components
- [ ] Property selection component
- [ ] Issue description form
- [ ] Timeline configuration
- [ ] Preferences form
- [ ] Form validation system

**Dependencies**: Wizard framework, validation library
**Testing**: Form validation, user experience testing

### 6.4 Phase 4: Contractor Matching (Week 4-5)

#### Sprint 4.1: Matching Algorithm
- [ ] Contractor eligibility filtering
- [ ] Scoring algorithm implementation
- [ ] Geographic radius calculations
- [ ] Availability checking
- [ ] Performance metrics integration

**Dependencies**: Contractor database, geolocation services
**Testing**: Algorithm accuracy testing, performance testing

#### Sprint 4.2: Invitation System
- [ ] Notification dispatch service
- [ ] Multi-channel messaging
- [ ] Staggered invitation waves
- [ ] Response tracking
- [ ] Follow-up automation

**Dependencies**: Matching algorithm, notification services
**Testing**: Notification delivery, response tracking

### 6.5 Phase 5: AI Integration (Week 5-6)

#### Sprint 5.1: SmartScope Integration
- [ ] Scope analysis API integration
- [ ] Category suggestion system
- [ ] Budget estimation service
- [ ] Timeline prediction
- [ ] Requirements analysis

**Dependencies**: AI service APIs, project data
**Testing**: AI accuracy testing, response time testing

#### Sprint 5.2: Intelligent Features
- [ ] Auto-categorization
- [ ] Smart contractor matching
- [ ] Personalized notifications
- [ ] Predictive analytics
- [ ] Learning system integration

**Dependencies**: SmartScope integration, user behavior data
**Testing**: Feature accuracy testing, user acceptance testing

### 6.6 Phase 6: Mobile Optimization (Week 6-7)

#### Sprint 6.1: Mobile-First UI
- [ ] Responsive design implementation
- [ ] Touch-friendly interactions
- [ ] Swipe navigation
- [ ] Camera integration
- [ ] Voice input features

**Dependencies**: Core UI components, mobile APIs
**Testing**: Cross-device testing, accessibility testing

#### Sprint 6.2: Performance Optimization
- [ ] Bundle size optimization
- [ ] Image lazy loading
- [ ] API response caching
- [ ] Offline draft capability
- [ ] Progressive loading

**Dependencies**: Mobile UI, caching infrastructure
**Testing**: Performance testing, offline testing

### 6.7 Phase 7: Integration & Testing (Week 7-8)

#### Sprint 7.1: End-to-End Integration
- [ ] Complete workflow testing
- [ ] Cross-component integration
- [ ] Data consistency validation
- [ ] Error handling verification
- [ ] Performance optimization

**Dependencies**: All previous phases
**Testing**: Full system testing, load testing

#### Sprint 7.2: Production Readiness
- [ ] Security audit
- [ ] Performance monitoring
- [ ] Analytics integration
- [ ] Documentation completion
- [ ] Deployment preparation

**Dependencies**: Complete system, monitoring tools
**Testing**: Security testing, production simulation

## 7. Testing Strategy & Checkpoints

### 7.1 Testing Checkpoints by Phase

#### Database Testing
```sql
-- Test data consistency
INSERT INTO projects (property_id, property_manager_id, title, description, category, urgency_level, bid_deadline)
VALUES ('test-property-id', 'test-user-id', 'Test Project', 'Test Description', 'plumbing', 'urgent', NOW() + INTERVAL '2 days');

-- Test constraints
-- Should fail: bid_deadline in past
-- Should fail: description too long
-- Should fail: invalid category
```

#### API Testing
```typescript
// Test project creation flow
describe('Project Creation API', () => {
  test('should create project with valid data', async () => {
    const response = await request(app)
      .post('/api/projects')
      .send(validProjectData)
      .expect(201);
    
    expect(response.body.id).toBeDefined();
    expect(response.body.status).toBe('draft');
  });
  
  test('should reject invalid data', async () => {
    const response = await request(app)
      .post('/api/projects')
      .send(invalidProjectData)
      .expect(400);
    
    expect(response.body.error.field_errors).toBeDefined();
  });
});
```

#### Frontend Testing
```typescript
// Test wizard navigation
describe('Project Creation Wizard', () => {
  test('should navigate through all steps', async () => {
    render(<ProjectCreationWizard />);
    
    // Step 1: Property selection
    await userEvent.selectOptions(screen.getByLabelText('Property'), 'property-1');
    await userEvent.click(screen.getByText('Next'));
    
    // Step 2: Issue description
    await userEvent.type(screen.getByLabelText('Title'), 'Test Project');
    await userEvent.type(screen.getByLabelText('Description'), 'Test description');
    await userEvent.click(screen.getByText('Next'));
    
    // Continue through all steps...
    expect(screen.getByText('Review & Publish')).toBeInTheDocument();
  });
});
```

### 7.2 Performance Benchmarks

```typescript
const performanceTargets = {
  project_creation_time: '< 120 seconds', // Under 2 minutes
  api_response_time: '< 500ms', // API calls
  file_upload_time: '< 5 seconds per photo',
  contractor_matching_time: '< 3 seconds',
  notification_dispatch_time: '< 30 seconds',
  
  // User experience metrics
  time_to_first_interaction: '< 2 seconds',
  step_transition_time: '< 200ms',
  form_validation_feedback: '< 100ms'
};

// Performance testing
describe('Performance Tests', () => {
  test('project creation under 2 minutes', async () => {
    const startTime = Date.now();
    
    // Simulate complete project creation flow
    await createCompleteProject();
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    expect(duration).toBeLessThan(120000); // 2 minutes
  });
});
```

## 8. Security Considerations

### 8.1 Data Validation & Sanitization

```typescript
// Input validation service
class InputValidationService {
  static validateProjectInput(input: any): CreateProjectRequest {
    // Sanitize HTML content
    const sanitizedInput = {
      ...input,
      title: DOMPurify.sanitize(input.title),
      description: DOMPurify.sanitize(input.description),
      hazards_notes: DOMPurify.sanitize(input.hazards_notes || ''),
      work_hour_restrictions: DOMPurify.sanitize(input.work_hour_restrictions || '')
    };
    
    // Validate against schema
    const result = ProjectValidationSchema.safeParse(sanitizedInput);
    
    if (!result.success) {
      throw new ValidationError(result.error.issues);
    }
    
    return result.data;
  }
  
  static validateFileUpload(file: File): void {
    // File type validation
    const allowedTypes = [
      'image/jpeg', 'image/png', 'image/webp',
      'video/mp4', 'video/quicktime'
    ];
    
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type');
    }
    
    // File size validation
    const maxSizes = {
      image: 10 * 1024 * 1024, // 10MB
      video: 100 * 1024 * 1024 // 100MB
    };
    
    const maxSize = file.type.startsWith('image/') 
      ? maxSizes.image 
      : maxSizes.video;
    
    if (file.size > maxSize) {
      throw new Error('File too large');
    }
    
    // Filename sanitization
    const sanitizedName = file.name
      .replace(/[^a-zA-Z0-9.-]/g, '_')
      .slice(0, 255);
    
    if (sanitizedName !== file.name) {
      // Create new File object with sanitized name
      return new File([file], sanitizedName, { type: file.type });
    }
  }
}
```

### 8.2 Authorization Framework

```typescript
// Resource-based authorization
class ProjectAuthorizationService {
  static async canCreateProject(userId: string): Promise<boolean> {
    // Check rate limits
    const todayCount = await this.getProjectCountToday(userId);
    if (todayCount >= 10) { // Max 10 projects per day
      throw new Error('Daily project creation limit exceeded');
    }
    
    // Check user role
    const user = await this.getUser(userId);
    return user.role === 'property_manager';
  }
  
  static async canViewProject(userId: string, projectId: string): Promise<boolean> {
    const project = await this.getProject(projectId);
    const user = await this.getUser(userId);
    
    // Property manager can view their own projects
    if (user.role === 'property_manager') {
      return project.property_manager_id === userId;
    }
    
    // Contractors can view projects they're invited to
    if (user.role === 'contractor') {
      const invitation = await this.getInvitation(projectId, userId);
      return invitation !== null;
    }
    
    return false;
  }
  
  static async canUploadMedia(userId: string, projectId: string): Promise<boolean> {
    const project = await this.getProject(projectId);
    
    // Only project owner can upload media
    // Only during draft or open_for_bids status
    return project.property_manager_id === userId && 
           ['draft', 'open_for_bids'].includes(project.status);
  }
}
```

### 8.3 Security Headers & Configuration

```typescript
// Express security configuration
const securityConfig = {
  helmet: {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        imgSrc: ["'self'", "*.supabase.co", "data:"],
        scriptSrc: ["'self'", "'unsafe-inline'"], // For development only
        styleSrc: ["'self'", "'unsafe-inline'"],
        connectSrc: ["'self'", "*.supabase.co"],
        mediaSrc: ["'self'", "*.supabase.co"]
      }
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    }
  },
  
  rateLimiting: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP'
  },
  
  cors: {
    origin: process.env.NODE_ENV === 'production' 
      ? ['https://instabids.com'] 
      : ['http://localhost:5173'],
    credentials: true
  }
};
```

## 9. Monitoring & Analytics

### 9.1 Performance Monitoring

```typescript
// Performance tracking service
class PerformanceMonitoringService {
  static trackProjectCreationFlow(userId: string): FlowTracker {
    return {
      startTime: Date.now(),
      steps: {},
      
      trackStep(stepName: string, duration: number): void {
        this.steps[stepName] = {
          duration,
          timestamp: Date.now()
        };
      },
      
      complete(): void {
        const totalDuration = Date.now() - this.startTime;
        
        // Send metrics to analytics service
        analytics.track('project_creation_completed', {
          user_id: userId,
          total_duration: totalDuration,
          steps: this.steps,
          success: true
        });
        
        // Alert if over target time
        if (totalDuration > 120000) { // 2 minutes
          logger.warn('Project creation exceeded target time', {
            user_id: userId,
            duration: totalDuration
          });
        }
      }
    };
  }
}

// Usage in components
const useProjectCreationTracking = () => {
  const tracker = useRef<FlowTracker>();
  
  const startTracking = useCallback(() => {
    tracker.current = PerformanceMonitoringService.trackProjectCreationFlow(userId);
  }, [userId]);
  
  const trackStep = useCallback((stepName: string, startTime: number) => {
    const duration = Date.now() - startTime;
    tracker.current?.trackStep(stepName, duration);
  }, []);
  
  return { startTracking, trackStep };
};
```

### 9.2 Business Metrics

```typescript
// Key business metrics tracking
const businessMetrics = {
  project_creation: {
    // Success metrics
    completion_rate: 'Projects published / Projects started',
    average_creation_time: 'Mean time from start to publish',
    step_abandonment_rate: 'Users leaving at each step',
    
    // Quality metrics
    projects_with_bids: 'Projects receiving 1+ bids',
    average_bids_per_project: 'Mean bid count per project',
    first_bid_time: 'Time to first bid received',
    
    // User experience
    user_satisfaction: 'Post-creation survey scores',
    feature_usage: 'Usage of optional features',
    mobile_vs_desktop: 'Creation method preferences'
  },
  
  contractor_matching: {
    match_accuracy: 'Relevant contractors in results',
    invitation_response_rate: 'Contractors responding to invites',
    bid_conversion_rate: 'Invites converting to bids',
    match_algorithm_performance: 'Quality of auto-matches'
  }
};
```

## 10. Future Enhancement Roadmap

### 10.1 Short-term Enhancements (3-6 months)

#### AI-Powered Project Templates
```typescript
// Auto-generate project templates based on historical data
interface ProjectTemplate {
  id: string;
  name: string;
  category: ProjectCategory;
  confidence_score: number;
  template_data: {
    title_suggestions: string[];
    description_template: string;
    typical_timeline: TimelineEstimate;
    budget_range: BudgetRangeType;
    common_requirements: string[];
  };
  usage_analytics: {
    usage_count: number;
    success_rate: number;
    average_bid_count: number;
  };
}

// Template suggestion service
class ProjectTemplateService {
  async suggestTemplates(
    propertyId: string,
    initialDescription?: string
  ): Promise<ProjectTemplate[]> {
    // Analyze property history
    const propertyHistory = await this.getPropertyProjectHistory(propertyId);
    
    // Use AI to suggest relevant templates
    const suggestions = await this.aiService.generateTemplates({
      property_history: propertyHistory,
      description_hint: initialDescription,
      seasonal_patterns: this.getSeasonalPatterns()
    });
    
    return suggestions.sort((a, b) => b.confidence_score - a.confidence_score);
  }
}
```

#### Advanced Contractor Analytics
```typescript
// Contractor performance analytics for better matching
interface ContractorAnalytics {
  contractor_id: string;
  performance_metrics: {
    response_pattern: {
      average_response_time: number;
      response_time_by_urgency: Record<UrgencyType, number>;
      response_rate_by_category: Record<ProjectCategory, number>;
    };
    bid_patterns: {
      average_bid_amount: number;
      bid_competitiveness: number;
      win_rate: number;
      typical_project_size: BudgetRangeType[];
    };
    quality_indicators: {
      completion_rate: number;
      on_time_completion_rate: number;
      customer_satisfaction: number;
      repeat_customer_rate: number;
    };
  };
  predictive_scores: {
    likelihood_to_respond: number;
    likelihood_to_win: number;
    project_match_score: number;
  };
}
```

### 10.2 Medium-term Enhancements (6-12 months)

#### Multi-Property Batch Projects
```typescript
// Batch project creation for property managers with multiple properties
interface BatchProjectCreation {
  template_id: string;
  properties: string[];
  variations: {
    property_specific_notes: Record<string, string>;
    custom_timelines: Record<string, TimelineOverride>;
    budget_adjustments: Record<string, BudgetRangeType>;
  };
  stagger_settings: {
    release_schedule: 'immediate' | 'staggered' | 'scheduled';
    interval_hours?: number;
    specific_dates?: Record<string, string>;
  };
}

// Seasonal maintenance scheduling
interface SeasonalScheduling {
  maintenance_type: 'hvac_tune_up' | 'gutter_cleaning' | 'landscaping';
  properties: string[];
  schedule_pattern: {
    frequency: 'monthly' | 'quarterly' | 'biannual' | 'annual';
    preferred_months: number[];
    advance_notice_days: number;
  };
  auto_creation_rules: {
    create_project_days_before: number;
    auto_invite_preferred_contractors: boolean;
    default_timeline: TimelineSettings;
  };
}
```

#### Integration with Property Management Systems
```typescript
// Work order system integration
interface WorkOrderIntegration {
  pms_system: 'yardi' | 'appfolio' | 'buildium' | 'custom';
  sync_settings: {
    auto_create_from_work_orders: boolean;
    sync_completion_status: boolean;
    update_tenant_notifications: boolean;
  };
  field_mapping: {
    tenant_id: string;
    unit_number: string;
    priority_level: string;
    category_mapping: Record<string, ProjectCategory>;
  };
}

// Tenant notification integration
interface TenantNotificationSystem {
  notification_triggers: {
    project_created: boolean;
    contractor_assigned: boolean;
    work_scheduled: boolean;
    work_completed: boolean;
  };
  communication_channels: {
    email: boolean;
    sms: boolean;
    in_app: boolean;
    portal_message: boolean;
  };
  custom_templates: {
    language_preferences: string[];
    branded_templates: boolean;
    tenant_portal_integration: boolean;
  };
}
```

### 10.3 Long-term Vision (12+ months)

#### Predictive Maintenance System
```typescript
// AI-driven predictive maintenance recommendations
interface PredictiveMaintenance {
  property_analytics: {
    equipment_age: Record<string, number>;
    maintenance_history: MaintenanceRecord[];
    failure_patterns: FailurePattern[];
    seasonal_trends: SeasonalTrend[];
  };
  predictions: {
    upcoming_issues: PredictedIssue[];
    optimal_timing: MaintenanceWindow[];
    cost_projections: CostProjection[];
    contractor_recommendations: ContractorRecommendation[];
  };
  automation_settings: {
    auto_schedule_routine: boolean;
    proactive_notifications: boolean;
    budget_approval_workflows: boolean;
  };
}

// IoT integration for real-time monitoring
interface IoTIntegration {
  sensor_data: {
    hvac_performance: HVACMetrics;
    water_leak_detection: LeakSensor[];
    energy_consumption: EnergyMetrics;
    security_systems: SecurityStatus;
  };
  alert_thresholds: {
    temperature_variance: number;
    humidity_levels: { min: number; max: number };
    energy_spike_percentage: number;
    leak_detection_sensitivity: number;
  };
  automated_responses: {
    emergency_shutoffs: boolean;
    contractor_auto_dispatch: boolean;
    tenant_notifications: boolean;
    priority_escalation: boolean;
  };
}
```

---

## Implementation Summary

This technical implementation plan provides a comprehensive roadmap for building the InstaBids project creation feature with the following key characteristics:

1. **Database-First Design**: Robust schema with proper constraints, indexes, and relationships
2. **API-Centric Architecture**: RESTful APIs with clear request/response schemas and comprehensive error handling
3. **Mobile-Optimized Frontend**: React-based wizard with responsive design and progressive enhancement
4. **Secure File Upload**: Multi-stage upload process with validation, compression, and security measures
5. **AI-Enhanced Matching**: Smart contractor discovery and personalized notifications
6. **Performance-Focused**: Sub-2-minute creation target with optimized queries and caching
7. **Scalable Foundation**: Modular design supporting future enhancements and integrations

The implementation follows a phased approach with clear dependencies, testing checkpoints, and measurable success criteria. Each phase builds upon the previous while maintaining system stability and user experience quality.

This plan serves as both a technical specification for developers and a project management tool for tracking progress against the goal of enabling property managers to create maintenance projects in under 2 minutes with automatic contractor matching and invitation.