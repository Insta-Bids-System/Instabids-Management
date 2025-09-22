-- Seed data for SmartScope tables aligning with FastAPI service contracts
-- Run in Supabase SQL editor before executing SmartScope end-to-end tests

INSERT INTO smartscope_analyses (
    project_id,
    photo_urls,
    primary_issue,
    severity,
    category,
    scope_items,
    materials,
    estimated_hours,
    safety_notes,
    additional_observations,
    confidence_score,
    metadata,
    processing_status,
    openai_response_raw
)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    ARRAY['https://example.com/photo-1.jpg', 'https://example.com/photo-2.jpg'],
    'Water leak under sink',
    'High',
    'Plumbing',
    '[{"title": "Replace P-trap", "description": "Remove and install new trap", "trade": "Plumbing", "materials": ["1.5\" PVC P-trap"], "safety_notes": ["Turn off water"], "estimated_hours": 1.5}]'::jsonb,
    '[{"name": "PVC P-trap", "quantity": "1", "specifications": "1.5 inch"}]'::jsonb,
    1.5,
    'Place bucket before removing trap',
    '["Inspect cabinet base for damage"]'::jsonb,
    0.92,
    '{"model_version": "gpt-4.1-mini", "tokens_used": 220, "processing_time_ms": 2800, "requested_by": "22222222-2222-2222-2222-222222222222"}'::jsonb,
    'completed',
    '{"response": {"ok": true}, "metadata": {"model_version": "gpt-4.1-mini", "tokens_used": 220}}'::jsonb
)
ON CONFLICT DO NOTHING;

INSERT INTO smartscope_feedback (
    analysis_id,
    user_id,
    feedback_type,
    accuracy_rating,
    scope_corrections,
    material_corrections,
    time_corrections,
    comments
)
VALUES (
    (SELECT id FROM smartscope_analyses LIMIT 1),
    '22222222-2222-2222-2222-222222222222',
    'property_manager',
    5,
    '{"add": ["Check dishwasher connection"]}'::jsonb,
    '{}'::jsonb,
    0.5,
    'Add inspection of dishwasher supply line'
)
ON CONFLICT DO NOTHING;

INSERT INTO smartscope_costs (
    analysis_id,
    api_cost,
    tokens_used,
    processing_time_ms
)
VALUES (
    (SELECT id FROM smartscope_analyses LIMIT 1),
    0.38,
    220,
    2800
)
ON CONFLICT DO NOTHING;