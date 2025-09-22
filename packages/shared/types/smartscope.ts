/**
 * TypeScript interfaces for SmartScope AI analysis workflows.
 * Mirrors the Python Pydantic models in api/models/smartscope.py
 */

export const SMARTSCOPE_SEVERITIES = ["Emergency", "High", "Medium", "Low"] as const;
export const SMARTSCOPE_SCOPE_ITEM_KEYS = [
  "title",
  "description",
  "trade",
  "materials",
  "safety_notes",
  "estimated_hours",
] as const;
export const SMARTSCOPE_MATERIAL_KEYS = [
  "name",
  "quantity",
  "specifications",
] as const;
export const SMARTSCOPE_METADATA_KEYS = [
  "processing_status",
  "model_version",
  "tokens_used",
  "api_cost",
  "processing_time_ms",
  "requested_by",
] as const;
export type SmartScopeSeverity = typeof SMARTSCOPE_SEVERITIES[number];

/**
 * Represents a single actionable scope item returned by the AI.
 */
export interface ScopeItem {
  /** Human readable title summarising the work */
  title: string;
  /** Detailed set of instructions for contractors */
  description: string;
  /** Primary trade responsible for this line item */
  trade?: string;
  /** Recommended materials or products required to complete the work */
  materials: string[];
  /** Relevant safety callouts for technicians */
  safety_notes: string[];
  /** Estimated labour hours to complete this item */
  estimated_hours?: number;
}

/**
 * Structured material requirements for the analysis.
 */
export interface MaterialItem {
  name: string;
  quantity?: string;
  /** Brand, grade or other specification details */
  specifications?: string;
}

/**
 * Payload required to trigger a SmartScope AI analysis run.
 */
export interface AnalysisRequest {
  project_id: string;
  photo_urls: string[];
  /** Residential, Commercial, etc */
  property_type: string;
  /** Location inside the property such as Kitchen */
  area: string;
  /** User reported description of the problem */
  reported_issue: string;
  /** Maintenance category e.g. Plumbing */
  category: string;
  /** Organisation requesting the analysis */
  organization_id?: string;
  /** User that initiated the request */
  requested_by?: string;
  /** Optional priority level */
  priority?: string;
}

/**
 * Additional metadata captured during processing.
 */
export interface AnalysisMetadata {
  processing_status: string;
  model_version: string;
  tokens_used?: number;
  api_cost?: number;
  processing_time_ms?: number;
  requested_by?: string;
}

/**
 * Represents a SmartScope analysis record returned to clients.
 */
export interface SmartScopeAnalysis {
  id: string;
  project_id: string;
  photo_urls: string[];
  primary_issue: string;
  severity: SmartScopeSeverity;
  category: string;
  scope_items: ScopeItem[];
  materials: MaterialItem[];
  estimated_hours?: number;
  safety_notes?: string;
  additional_observations: string[];
  confidence_score: number; // 0.0 to 1.0
  openai_response_raw: Record<string, any>;
  metadata: AnalysisMetadata;
  created_at: string; // ISO timestamp
  updated_at: string; // ISO timestamp
}

/**
 * Internal helper model when persisting new analysis records.
 */
export interface SmartScopeAnalysisCreate {
  project_id: string;
  photo_urls: string[];
  primary_issue: string;
  severity: string;
  category: string;
  scope_items: Record<string, any>[];
  materials: Record<string, any>[];
  estimated_hours?: number;
  safety_notes?: string;
  additional_observations: string[];
  confidence_score: number;
  openai_response_raw: Record<string, any>;
  metadata: Record<string, any>;
}

/**
 * Feedback payload submitted by property managers or contractors.
 */
export interface FeedbackRequest {
  feedback_type: string;
  accuracy_rating: number; // 1 to 5
  scope_corrections: Record<string, any>;
  material_corrections: Record<string, any>;
  time_corrections?: number;
  comments?: string;
}

/**
 * Feedback record stored in the database.
 */
export interface FeedbackRecord {
  id: string;
  analysis_id: string;
  user_id?: string;
  feedback_type: string;
  accuracy_rating: number;
  scope_corrections: Record<string, any>;
  material_corrections: Record<string, any>;
  time_corrections?: number;
  comments?: string;
  created_at: string; // ISO timestamp
}

/**
 * Aggregated analytics for SmartScope performance dashboards.
 */
export interface AccuracyMetrics {
  total_analyses: number;
  average_confidence: number;
  average_accuracy_rating?: number;
  category_accuracy: Record<string, number>;
  last_feedback_at?: string; // ISO timestamp
  improvements_last_30_days?: number;
}

/**
 * Paginated listing of SmartScope analyses.
 */
export interface AnalysisListResponse {
  analyses: SmartScopeAnalysis[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}