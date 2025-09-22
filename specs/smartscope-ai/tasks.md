# SmartScope AI Task Tracker

_Last reviewed: updated after full code audit of `/api`, `/packages/shared`, `migrations/004_marketplace_core.sql`, and frontend folders._

## Current Implementation Snapshot
- **Domain models are in place.** `api/models/smartscope.py` defines rich Pydantic models for requests, responses, feedback, and analytics, mirrored by `packages/shared/types/smartscope.ts` for the web stack.
- **Core analysis service exists.** `api/services/openai_vision.py` fetches images over HTTP, applies EXIF auto-orientation, resizing, and light enhancement, constructs multi-image prompts, parses JSON responses, and estimates fallback confidence.
- **Service orchestration and API routes work in-memory.** `api/services/smartscope_service.py` coordinates analysis, Supabase persistence, feedback capture, analytics aggregation, and cost tracking; `api/routers/smartscope.py` exposes analyze/get/list/feedback/analytics endpoints guarded by `get_current_user`.
- **Cost monitoring helpers are written.** `api/services/cost_monitor.py` estimates token spend and can compile budget usage, but Supabase persistence for costs is missing.
- **Automated coverage is limited to unit tests.** `api/tests/test_smartscope_service.py` exercises the vision service, service orchestration, cost monitor, and analytics with fake backends—no live Supabase or API tests.
- **Schema and frontend gaps remain.** The shipped Supabase migration defines `smartscope_analyses`/`smartscope_feedback` tables whose shapes do not match the service payloads, there is no `smartscope_costs` table, no SmartScope UI in `web/`, and no project-creation automation.

---

## Task Breakdown

### 1. Domain Models & Shared Contracts
- [x] Maintain synchronized request/response/feedback models between `api/models/smartscope.py` and `packages/shared/types/smartscope.ts`.
- [ ] Document and enforce the canonical field names (severity values, metadata keys, trade/material structures) once persistence is realigned so both codebases stay in lockstep.

### 2. Database Schema & Persistence
- [ ] **Align `smartscope_analyses` schema with the service.** Current migration stores `analyzed_media_ids`/`scope_items`/`materials_needed` as arrays and enforces `project_id` uniqueness, while the service inserts JSON payloads and expects multiple analyses per project. Decide on the canonical structure and update both the migration and service accordingly.
- [ ] **Fix `smartscope_feedback` column mismatches.** The migration expects fields like `feedback_by`, `missing_items`, and rating breakdowns, but the service writes `user_id`, `scope_corrections`, and `material_corrections`. Update schema and persistence code so inserts succeed.
- [ ] **Create and migrate the `smartscope_costs` table.** `CostMonitor.track_analysis_cost` already writes to this table; add the missing migration with appropriate indexes and RLS policies.
- [ ] Add row-level security policies for SmartScope tables that match the access patterns used by the API (`get_current_user`, organization scoping, etc.).
- [ ] Provide seed or fixture data scripts to validate Supabase interactions locally (mock data for analyses, feedback, costs).

### 3. Vision & Prompting Pipeline
- [x] Multi-image preprocessing, prompt construction, and JSON parsing via `OpenAIVisionService`.
- [ ] Add defensive retries, error classification, and optional circuit-breaker/rate-limiting so repeated OpenAI failures or quota limits do not take down the endpoint.
- [ ] Introduce response caching (e.g., keyed by project+photo hash) to avoid re-analyzing identical media when users retry.
- [ ] Implement richer image heuristics (multi-angle grouping, blur detection) to surface low-quality inputs before invoking the model.
- [ ] Capture telemetry (latency, tokens, confidence) for observability dashboards once Supabase schema is aligned.

### 4. API Layer & Orchestration
- [x] `POST /smartscope/analyze`, `GET /smartscope/{analysis_id}`, `GET /smartscope/project/{project_id}`, `POST /smartscope/{analysis_id}/feedback`, and `GET /smartscope/analytics/accuracy` implemented with basic error handling.
- [ ] Build an update endpoint for human edits/approvals, persisting reviewer metadata and change history as envisioned in the spec.
- [ ] Provide a status/polling endpoint if analyses transition to asynchronous processing (see Task 7), or document that processing is synchronous.
- [ ] Harden Supabase error handling: map known failure modes (permission errors, schema mismatches) to actionable API responses and alerts.
- [ ] Enforce organization-level authorization checks so users can only access analyses tied to their properties/projects.

### 5. Cost Monitoring & Operational Safeguards
- [x] Token-to-cost estimation and budget summary helpers exist in `CostMonitor`.
- [ ] Wire cost tracking to real persistence once the `smartscope_costs` table exists; surface cost data in analytics responses.
- [ ] Implement budget alerting integrations (email/Slack/webhooks) instead of log-only warnings.
- [ ] Add configuration and enforcement for per-organization or per-user spending limits if required by business rules.

### 6. Feedback, Analytics & Learning
- [x] Feedback submission endpoint and aggregated confidence/accuracy metrics calculations (in-memory) exist.
- [ ] Ensure Supabase feedback writes succeed after schema alignment; add migrations/tests covering the analytics queries against real data.
- [ ] Implement learning/calibration loop: adjust confidence thresholds or prompt templates based on accumulated feedback, as described in `spec.md`.
- [ ] Provide category-level accuracy dashboards and trend analysis beyond simple averages (e.g., 30-day improvements, variance).
- [ ] Design data retention and anonymization policies for feedback payloads if required for compliance.

### 7. Integrations & Automation
- [ ] Trigger SmartScope automatically from project creation or media upload events (currently only manual API invocation is available).
- [ ] Connect SmartScope outputs to contractor matching and quote validation workflows (populate downstream tables, send notifications).
- [ ] Define background job or queue strategy if analyses should run asynchronously or be retried outside the request lifecycle.
- [ ] Document and implement failure compensation steps (e.g., fall back to manual review when AI fails).

### 8. Frontend Experience
- [ ] Build SmartScope UI modules (`AnalysisDisplay`, `ScopeEditor`, contractor view, feedback forms) in `web/src/components/` with data wiring to the API.
- [ ] Add routing/state management on the frontend for listing analyses, reviewing details, and submitting feedback.
- [ ] Implement real-time updates or polling in the UI to reflect analysis status, cost usage, and feedback history.
- [ ] Ensure accessibility, responsive design, and error states follow the design system.

### 9. Testing, Tooling & QA
- [x] Unit tests cover service orchestration, cost monitoring, and prompt parsing using fakes.
- [ ] Add integration tests hitting the FastAPI router with a mocked Supabase service to validate request/response contracts end-to-end.
- [ ] Create contract tests ensuring TypeScript and Python models stay in sync (e.g., schema snapshots or shared fixtures).
- [ ] Introduce performance/load tests to verify latency (<15s) and concurrency targets once asynchronous processing or caching is added.
- [ ] Add resilience tests (OpenAI downtime, Supabase failures, malformed media) to guarantee graceful degradation.
- [ ] Automate linting/type-checking for new frontend/backoffice modules when they land.

### 10. Documentation & Operational Readiness
- [ ] Update `README.md`/`PROGRESS.md` with the true SmartScope status once schema fixes land.
- [ ] Write runbooks covering API key rotation, OpenAI quota monitoring, and Supabase incident response.
- [ ] Provide onboarding docs for property managers/contractors explaining SmartScope workflows once the UI and automation are built.

---

This tracker reflects the current repository state and outstanding work required to deliver the SmartScope AI feature end-to-end. Update it as tasks are completed so it remains the source of truth for planning and execution.
