/**
 * Project management types for InstaBids Management platform
 */

export enum ProjectCategory {
  MAINTENANCE = "maintenance",
  REPAIR = "repair",
  IMPROVEMENT = "improvement",
  EMERGENCY = "emergency",
  INSPECTION = "inspection",
  INSTALLATION = "installation",
  RENOVATION = "renovation",
  COSMETIC = "cosmetic",
}

export enum ProjectPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent",
  EMERGENCY = "emergency",
}

export enum ProjectStatus {
  PLANNING = "planning",
  PENDING_APPROVAL = "pending_approval",
  APPROVED = "approved",
  IN_PROGRESS = "in_progress",
  ON_HOLD = "on_hold",
  COMPLETED = "completed",
  CANCELLED = "cancelled",
  REQUIRES_REVIEW = "requires_review",
}

export interface Project {
  id: string;
  title: string;
  description?: string;
  property_id: string;
  category: ProjectCategory;
  priority: ProjectPriority;
  status: ProjectStatus;
  budget?: number;
  estimated_hours?: number;
  actual_hours?: number;
  area?: string;
  reported_issue?: string;
  photo_urls: string[];
  contractor_id?: string;
  assigned_users: string[];
  due_date?: string;
  completed_date?: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  
  // Related entities (populated in some contexts)
  property?: {
    id: string;
    name: string;
    address: string;
  };
  contractor?: {
    id: string;
    name: string;
    email: string;
    phone?: string;
  };
  smartscope_analysis?: {
    id: string;
    confidence_score: number;
    primary_issue: string;
    severity: string;
    materials: MaterialItem[];
    scope_items: ScopeItem[];
  };
}

export interface CreateProjectRequest {
  title: string;
  description?: string;
  property_id: string;
  category: ProjectCategory;
  priority: ProjectPriority;
  status: ProjectStatus;
  budget?: number;
  estimated_hours?: number;
  area?: string;
  reported_issue?: string;
  photo_urls: string[];
  contractor_id?: string;
  assigned_users?: string[];
  due_date?: string;
}

export interface UpdateProjectRequest {
  title?: string;
  description?: string;
  category?: ProjectCategory;
  priority?: ProjectPriority;
  status?: ProjectStatus;
  budget?: number;
  estimated_hours?: number;
  actual_hours?: number;
  area?: string;
  reported_issue?: string;
  photo_urls?: string[];
  contractor_id?: string;
  assigned_users?: string[];
  due_date?: string;
  completed_date?: string;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ProjectFilters {
  property_id?: string;
  category?: ProjectCategory;
  priority?: ProjectPriority;
  status?: ProjectStatus;
  contractor_id?: string;
  assigned_to?: string;
  created_after?: string;
  created_before?: string;
  due_after?: string;
  due_before?: string;
  search?: string;
}

// SmartScope AI related types
export interface ScopeItem {
  title: string;
  description: string;
  trade?: string;
  materials: string[];
  safety_notes: string[];
  estimated_hours?: number;
}

export interface MaterialItem {
  name: string;
  quantity?: string;
  specifications?: string;
}

export interface SmartScopeAnalysisRequest {
  project_id: string;
  photo_urls: string[];
  category: ProjectCategory;
  property_type: string;
  area: string;
  reported_issue: string;
}

export interface SmartScopeAnalysis {
  id: string;
  project_id: string;
  photo_urls: string[];
  primary_issue: string;
  severity: "Emergency" | "High" | "Medium" | "Low";
  category: ProjectCategory;
  scope_items: ScopeItem[];
  materials: MaterialItem[];
  estimated_hours?: number;
  safety_notes?: string;
  additional_observations: string[];
  confidence_score: number;
  created_at: string;
  updated_at: string;
  
  metadata: {
    processing_status: string;
    model_version: string;
    tokens_used?: number;
    api_cost?: number;
    processing_time_ms?: number;
  };
}

// Project activity tracking
export interface ProjectActivity {
  id: string;
  project_id: string;
  user_id: string;
  action: string;
  description: string;
  metadata?: Record<string, any>;
  created_at: string;
  
  user?: {
    id: string;
    name: string;
    email: string;
  };
}

// Project comments/notes
export interface ProjectComment {
  id: string;
  project_id: string;
  user_id: string;
  content: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
  
  user?: {
    id: string;
    name: string;
    email: string;
  };
}

export interface CreateProjectCommentRequest {
  content: string;
  is_internal?: boolean;
}

// Project file attachments
export interface ProjectFile {
  id: string;
  project_id: string;
  filename: string;
  file_url: string;
  file_size: number;
  file_type: string;
  uploaded_by: string;
  uploaded_at: string;
  
  uploader?: {
    id: string;
    name: string;
    email: string;
  };
}

export interface UploadProjectFileRequest {
  file: File;
  description?: string;
}

// Utility types
export type ProjectSortField = 
  | "created_at" 
  | "updated_at" 
  | "title" 
  | "priority" 
  | "status" 
  | "due_date" 
  | "budget";

export type SortDirection = "asc" | "desc";

export interface ProjectSort {
  field: ProjectSortField;
  direction: SortDirection;
}

// Dashboard/analytics types
export interface ProjectStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  overdue_projects: number;
  total_budget: number;
  spent_budget: number;
  average_completion_time: number;
  projects_by_status: Record<ProjectStatus, number>;
  projects_by_category: Record<ProjectCategory, number>;
  projects_by_priority: Record<ProjectPriority, number>;
}

export interface ProjectMetrics {
  completion_rate: number;
  average_budget_accuracy: number;
  average_time_accuracy: number;
  on_time_completion_rate: number;
  budget_variance: number;
  time_variance: number;
}

// Export all types for easier importing
export type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectListResponse,
  ProjectFilters,
  ProjectActivity,
  ProjectComment,
  CreateProjectCommentRequest,
  ProjectFile,
  UploadProjectFileRequest,
  ProjectSort,
  ProjectStats,
  ProjectMetrics,
  SmartScopeAnalysisRequest,
  SmartScopeAnalysis,
  ScopeItem,
  MaterialItem,
};