# Technical Implementation Plan: SmartScope AI

_Last audited: after full repository review of backend (`api/`), shared packages (`packages/shared`), migrations, and web code._

## 1. Current Architecture Snapshot

### 1.1 Service Topology
- **Backend framework**: FastAPI application under `api/`.
- **SmartScope router**: `api/routers/smartscope.py` exposes `analyze`, `get`, `list by project`, `feedback`, and `analytics` endpoints guarded by `get_current_user`.
- **Business logic**: `api/services/smartscope_service.py` orchestrates OpenAI calls, persistence, analytics aggregation, and cost monitoring.
- **Vision pipeline**: `api/services/openai_vision.py` downloads images, performs EXIF auto-orientation, resizing, and brightness/contrast tuning with Pillow, then crafts a multi-image prompt for `AsyncOpenAI`.
- **Shared contracts**: Pydantic models in `api/models/smartscope.py` mirror TypeScript types in `packages/shared/types/smartscope.ts`.
- **Persistence**: Supabase access is handled through the shared `SupabaseClient` helpers; existing migration `004_marketplace_core.sql` defines `smartscope_analyses` and `smartscope_feedback` tables but their schemas drift from the service payloads. No `smartscope_costs` table exists yet.

### 1.2 Operational State
- Requests are handled synchronously; there is no queue, cache, or background worker.
- Cost tracking is computed in-memory by `CostMonitor` with attempted writes to a missing `smartscope_costs` table.
- Unit tests in `api/tests/test_smartscope_service.py` validate service orchestration with fakes; there are no integration, Supabase, or frontend tests.
- The web frontend has no SmartScope UI modules.

## 2. Gap Analysis
| Area | Current Behaviour | Required Outcome |
|------|-------------------|------------------|
| Database schema | Arrays/constraints that do not match `SmartScopeService` payloads; missing `smartscope_costs`. | Align Supabase tables with API models (JSONB payloads, feedback shapes, dedicated costs table, RLS policies). |
| Error handling & resilience | Direct OpenAI call without retries, rate limiting, or caching. | Harden vision pipeline (retries, backoff, circuit-breaker, cached responses, telemetry). |
| API surface | CRUD limited to analyze/get/list/feedback/analytics. | Add update/approval endpoints, status polling (if async introduced), organization scoping, and richer Supabase error mapping. |
| Cost monitoring | `CostMonitor` estimates spend in-memory but cannot persist or alert; budgets unused. | Persist cost rows, surface budget telemetry, and integrate alerting/reporting hooks. |
| Integrations | Manual invocation only; no downstream wiring. | Trigger from project/media events, feed contractor matching & quote validation, define compensation strategies. |
| Frontend | No SmartScope components or routes. | Build analysis dashboards, feedback editor, and contractor-facing views. |
| QA & monitoring | Unit tests only; no observability. | Introduce integration/load/resilience tests, metrics, and alerting (latency, costs, accuracy). |

## 3. Implementation Roadmap

### Phase A – Schema & Contract Alignment
1. Design canonical Supabase schemas for analyses, feedback, and costs that reflect `SmartScopeService` models (JSONB payloads, foreign keys to projects/media/users).
2. Create migrations (including RLS policies) and update service persistence code accordingly.
3. Backfill/seed representative data for local testing; update shared TypeScript types if fields change.
4. Add integration tests that exercise FastAPI routes against a mocked Supabase layer to lock in request/response contracts.

### Phase B – Resilient Vision Pipeline
1. Extend `OpenAIVisionService` with retry/backoff, structured error classification, and optional circuit-breaking.
2. Implement deterministic request identifiers and caching for repeat analyses (e.g., hashing project+media IDs).
3. Capture telemetry (latency, tokens, cost) and persist via the new costs table; expose metrics via analytics endpoints.
4. Add image quality heuristics (blur detection, low-light warnings) and surface them in responses for UI display.

### Phase C – API Enhancements & Authorization
1. Add endpoints for human review updates (approve/edit analysis, override confidence) with audit metadata.
2. Introduce organization-level authorization checks leveraging project ownership, and ensure Supabase policies mirror them.
3. Harden Supabase error handling: catch permission/schema issues and map to actionable HTTP responses with logging/alerts.
4. Document synchronous vs. asynchronous behaviour; if asynchronous processing is required, define queue/background worker pattern and implement status polling.
5. Wire `CostMonitor` to the new Supabase tables, expose budget analytics endpoints, and configure alerting hooks once persistence succeeds.

### Phase D – Integrations & Frontend Delivery
1. Hook SmartScope analysis into project creation/media upload workflows (trigger analysis jobs, persist linkage).
2. Connect outputs to contractor matching and quote validation services; publish events or write to shared tables.
3. Build Vue components for analysis listing, detail review, feedback submission, and contractor views under `web/src/components/smartscope/` with corresponding routes/state management.
4. Implement real-time updates or polling in the UI, including cost usage and confidence trends.

### Phase E – Learning, Monitoring, and QA
1. Implement feedback ingestion jobs that adjust prompts/confidence thresholds (calibration loop) using Supabase data.
2. Provide analytics dashboards (category accuracy, 30-day trends, variance) through API endpoints and UI charts.
3. Wire budget alerting (email/Slack/webhooks) once cost persistence is live; enforce configurable spend limits.
4. Expand test suite: contract tests between Python/TypeScript models, load tests for concurrency, chaos tests for OpenAI/Supabase outages.
5. Publish runbooks covering OpenAI key rotation, quota monitoring, incident response, and SmartScope operational procedures.

## 4. Deliverables & Definition of Done
- Supabase schemas, policies, and migrations committed and verified via automated tests.
- FastAPI endpoints covering analysis lifecycle, with comprehensive authorization and error handling.
- Vision pipeline resilient to API failures and duplicate requests, with telemetry captured in Supabase.
- Frontend experience that allows property managers and contractors to review, edit, and trust SmartScope results.
- Integrations that automatically trigger analyses and feed downstream contractor matching/quote validation workflows.
- Monitoring, alerting, and documentation sufficient for operations to support SmartScope in production.
- Updated `spec.md`, `tasks.md`, and `PROGRESS.md` reflecting implementation status.

## 5. Open Questions / Dependencies
- Final decision on synchronous vs. asynchronous processing model (impacts queue requirements and API design).
- Business rules for cost budgets, alert thresholds, and who receives notifications.
- Data retention/privacy requirements for storing photos, analyses, and feedback.
- Alignment with contractor matching roadmap to ensure SmartScope outputs feed the right destinations.

---
This plan replaces outdated Node.js/queue assumptions with the actual Python/FastAPI stack and charts the work required to deliver the SmartScope AI feature end-to-end.
