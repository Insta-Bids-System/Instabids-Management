-- 005_smartscope_alignment.sql
-- Purpose: Align SmartScope tables with implemented FastAPI service contracts
-- Includes: schema realignment, feedback column fixes, cost tracking table, RLS policies

BEGIN;

-- Allow multiple analyses per project
ALTER TABLE smartscope_analyses
    DROP CONSTRAINT IF EXISTS smartscope_analyses_project_id_key;

-- Rename severity column to match API payloads
ALTER TABLE smartscope_analyses
    RENAME COLUMN severity_level TO severity;

-- Ensure severity stored as text
ALTER TABLE smartscope_analyses
    ALTER COLUMN severity TYPE TEXT;

-- Add missing columns used by the service layer
ALTER TABLE smartscope_analyses
    ADD COLUMN IF NOT EXISTS photo_urls TEXT[] DEFAULT '{}'::text[],
    ADD COLUMN IF NOT EXISTS category TEXT,
    ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS processing_status TEXT DEFAULT 'completed',
    ADD COLUMN IF NOT EXISTS openai_response_raw JSONB DEFAULT '{}'::jsonb;

-- Convert arrays to structured JSON for scope and materials payloads
ALTER TABLE smartscope_analyses
    ALTER COLUMN scope_items TYPE JSONB USING COALESCE(to_jsonb(scope_items), '[]'::jsonb);

ALTER TABLE smartscope_analyses
    RENAME COLUMN materials_needed TO materials;

ALTER TABLE smartscope_analyses
    ALTER COLUMN materials TYPE JSONB USING COALESCE(to_jsonb(materials), '[]'::jsonb);

ALTER TABLE smartscope_analyses
    ALTER COLUMN additional_observations TYPE JSONB USING COALESCE(to_jsonb(additional_observations), '[]'::jsonb);

-- Keep analysed media identifiers as JSON for flexibility when media tables expand
ALTER TABLE smartscope_analyses
    ALTER COLUMN analyzed_media_ids TYPE JSONB USING COALESCE(to_jsonb(analyzed_media_ids), '[]'::jsonb);

-- ---------------------------------------------------------------------------
-- Feedback table alignment
-- ---------------------------------------------------------------------------

ALTER TABLE smartscope_feedback
    RENAME COLUMN feedback_by TO user_id;

ALTER TABLE smartscope_feedback
    ALTER COLUMN user_id TYPE UUID USING user_id::uuid;

ALTER TABLE smartscope_feedback
    DROP COLUMN IF EXISTS missing_items,
    DROP COLUMN IF EXISTS incorrect_items,
    DROP COLUMN IF EXISTS scope_accuracy_rating,
    DROP COLUMN IF EXISTS materials_accuracy_rating,
    DROP COLUMN IF EXISTS time_estimate_accuracy_rating,
    DROP COLUMN IF EXISTS suggestions_for_improvement,
    DROP COLUMN IF EXISTS actual_scope_items,
    DROP COLUMN IF EXISTS actual_materials,
    DROP COLUMN IF EXISTS actual_duration_hours,
    DROP COLUMN IF EXISTS actual_cost,
    DROP COLUMN IF EXISTS general_comments;

ALTER TABLE smartscope_feedback
    ADD COLUMN IF NOT EXISTS scope_corrections JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS material_corrections JSONB DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS time_corrections NUMERIC(6,2),
    ADD COLUMN IF NOT EXISTS comments TEXT;

-- ---------------------------------------------------------------------------
-- Cost tracking table
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS smartscope_costs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES smartscope_analyses(id) ON DELETE CASCADE NOT NULL,
    api_cost DECIMAL(10,4) NOT NULL,
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_smartscope_costs_analysis_id ON smartscope_costs(analysis_id);
CREATE INDEX IF NOT EXISTS idx_smartscope_costs_created_at ON smartscope_costs(created_at);

-- ---------------------------------------------------------------------------
-- Row Level Security policies
-- ---------------------------------------------------------------------------

ALTER TABLE smartscope_costs ENABLE ROW LEVEL SECURITY;

-- Helper expression reused across policies
-- Users can access SmartScope data when they belong to the same organisation as the project property
CREATE OR REPLACE VIEW smartscope_project_access AS
SELECT
    sa.id AS analysis_id,
    p.id AS project_id,
    prop.organization_id
FROM smartscope_analyses sa
JOIN projects p ON p.id = sa.project_id
JOIN properties prop ON prop.id = p.property_id;

-- Analyses policies
CREATE POLICY IF NOT EXISTS "Users view SmartScope analyses for their organisation"
ON smartscope_analyses
FOR SELECT USING (
    EXISTS (
        SELECT 1
        FROM smartscope_project_access spa
        JOIN user_profiles up ON up.organization_id = spa.organization_id
        WHERE spa.analysis_id = smartscope_analyses.id
          AND up.id = auth.uid()
    )
);

CREATE POLICY IF NOT EXISTS "Users create SmartScope analyses for their organisation"
ON smartscope_analyses
FOR INSERT WITH CHECK (
    EXISTS (
        SELECT 1
        FROM smartscope_project_access spa
        JOIN user_profiles up ON up.organization_id = spa.organization_id
        WHERE spa.project_id = smartscope_analyses.project_id
          AND up.id = auth.uid()
    )
);

-- Feedback policies
CREATE POLICY IF NOT EXISTS "Users manage SmartScope feedback for their organisation"
ON smartscope_feedback
FOR ALL USING (
    EXISTS (
        SELECT 1
        FROM smartscope_project_access spa
        JOIN user_profiles up ON up.organization_id = spa.organization_id
        WHERE spa.analysis_id = smartscope_feedback.analysis_id
          AND up.id = auth.uid()
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM smartscope_project_access spa
        JOIN user_profiles up ON up.organization_id = spa.organization_id
        WHERE spa.analysis_id = smartscope_feedback.analysis_id
          AND up.id = auth.uid()
    )
);

-- Cost policies
CREATE POLICY IF NOT EXISTS "Users view SmartScope costs for their organisation"
ON smartscope_costs
FOR SELECT USING (
    EXISTS (
        SELECT 1
        FROM smartscope_project_access spa
        JOIN user_profiles up ON up.organization_id = spa.organization_id
        WHERE spa.analysis_id = smartscope_costs.analysis_id
          AND up.id = auth.uid()
    )
);

CREATE POLICY IF NOT EXISTS "Users create SmartScope costs for their organisation"
ON smartscope_costs
FOR INSERT WITH CHECK (
    EXISTS (
        SELECT 1
        FROM smartscope_project_access spa
        JOIN user_profiles up ON up.organization_id = spa.organization_id
        WHERE spa.analysis_id = smartscope_costs.analysis_id
          AND up.id = auth.uid()
    )
);

COMMIT;