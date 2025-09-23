# SmartScope AI Specification

_Last validated: repository audit covering `api/`, `packages/shared`, `migrations`, and `web/` directories._

## 1. Feature Overview
SmartScope AI analyzes property maintenance photos with OpenAI Vision, produces structured scopes of work, and captures feedback to improve accuracy over time. The initial FastAPI implementation provides the core analysis flow but significant gaps remain across persistence, integrations, and user experience. This specification documents what exists today and the requirements to deliver the production-ready feature.

## 2. Stakeholders & User Goals

### 2.1 Property Managers
- Receive AI-generated descriptions of maintenance issues.
- Edit or approve scopes before sharing with contractors.
- Track analysis confidence and cost impact per project.

### 2.2 Contractors
- Access standardized scopes, materials, and risk notes prior to bidding.
- Flag inaccuracies or missing work items to feed the learning loop.

### 2.3 Platform Operations
- Monitor SmartScope accuracy, latency, and spending.
- Ensure analyses integrate with project creation, contractor matching, and quote validation.
- Maintain audit trails for regulatory and quality purposes.

## 3. Current Implementation Summary
| Area | Status | Notes |
|------|--------|-------|
| Domain models | ✅ Implemented | Pydantic models in `api/models/smartscope.py` mirror TypeScript types in `packages/shared/types/smartscope.ts`.
| Vision pipeline | ✅ Implemented (baseline) | `OpenAIVisionService` handles HTTP fetch, EXIF auto-orientation, resizing, light enhancement, multi-image prompt creation, and JSON parsing.
| Service orchestration | ✅ Implemented (baseline) | `SmartScopeService` coordinates analysis, Supabase persistence, analytics aggregation, and cost estimation; exposed via FastAPI router.
| Cost monitoring | ⚠️ Partial | `CostMonitor` estimates spend but the target `smartscope_costs` table is missing; writes currently fail in real environments.
| Persistence schema | ❌ Incomplete | Supabase migration defines schemas incompatible with service payloads; no cost table or RLS policies tailored to SmartScope.
| Authorization | ❌ Missing | FastAPI endpoints rely solely on `get_current_user`; Supabase policies for SmartScope tables are absent, so cross-organization access is not prevented.
| Integrations | ❌ Missing | No automation from project creation/media upload, contractor matching, or quote workflows.
| Frontend UI | ❌ Missing | No SmartScope components/routes in the web app.
| Testing & QA | ⚠️ Partial | Unit tests with fakes exist; integration, load, and resilience coverage absent.

## 4. Functional Requirements
Each subsection includes the **Current State** and the **Required Outcome** to reach production readiness.

### 4.1 Photo Analysis Pipeline
- **Image Preprocessing**
  - Current: Auto-orientation, resizing, and brightness/contrast adjustment implemented.
  - Required: Add blur/low-light detection, quality scoring, and warnings surfaced in the API response.
- **AI Request Handling**
  - Current: Synchronous OpenAI Vision request with static prompt builder, no retry logic.
  - Required: Structured prompt templates per category, retry/backoff with error classification, optional circuit breaker, and response caching for duplicate analyses.
- **Scope Generation Output**
  - Current: Structured JSON containing issues, scope items, materials, confidence, and metadata persisted via Supabase client.
  - Required: Guarantee schema parity between API responses and Supabase tables; include telemetry (latency, tokens) and quality flags once persistence aligns.

### 4.2 Scope Enhancement & Feedback Loop
- **Human Review Workflow**
  - Current: Feedback endpoint stores corrections, but schema mismatch prevents real Supabase writes; no approval/update endpoint.
  - Required: Create update/approval APIs, persist reviewer metadata, maintain change history, and expose analytics on human adjustments.
- **Learning & Calibration**
  - Current: Accuracy analytics computed in-memory from cached data only.
  - Required: Aggregate feedback in Supabase, adjust prompt/thresholds over time, surface category-level accuracy trends, and provide configuration for confidence targets.

### 4.3 Persistence & Authorization
- **Database Schema**
  - Current: `smartscope_analyses` stores arrays incompatible with service JSON; `smartscope_feedback` column names differ; `smartscope_costs` absent.
  - Required: Migrate to JSONB payloads matching `SmartScopeService` models, add foreign keys to projects/media/users, create `smartscope_costs`, and enforce RLS policies aligned with organization scoping.
- **Authorization**
  - Current: FastAPI router relies on `get_current_user` but lacks organization-level checks; Supabase policies do not exist.
  - Required: Validate user access against project ownership and mirror logic in Supabase policies to prevent cross-organization leakage.

### 4.4 Integrations & Automation
- **Project & Media Triggers**
  - Current: Analyses executed manually through API.
  - Required: Automatic invocation on project creation or media upload, with idempotent handling to avoid duplicate work.
- **Downstream Workflows**
  - Current: No contractor matching or quote validation hooks.
  - Required: Publish SmartScope outputs to contractor matching services, quote comparison logic, and notifications for assigned parties.
- **Failure Handling**
  - Current: Errors bubble up to the client; no compensation strategy.
  - Required: Document/manual fallback path, alerting, and optional queue-based retries for failed analyses.

### 4.5 Frontend Experience
- **Analysis Review UI**
  - Current: Absent.
  - Required: Build Vue components (analysis list, detail view, scope editor, confidence display) and route integration under `web/src/components/smartscope/`.
- **Feedback Submission**
  - Current: No UI workflow.
  - Required: Enable property managers and contractors to submit corrections, view history, and monitor accuracy improvements.
- **Real-Time Updates**
  - Current: None.
  - Required: Implement polling or websocket updates for analysis status, cost consumption, and feedback acknowledgements.

## 5. Non-Functional Requirements
- **Performance**: Analysis requests should complete within 15 seconds P95 once telemetry is in place; UI updates must remain responsive under concurrent usage.
- **Reliability**: Introduce retries/backoff for OpenAI and Supabase interactions, plus monitoring/alerting for failures and budget overruns.
- **Security**: Enforce organization-level access, ensure media URLs are securely fetched, and handle sensitive data per privacy policies.
- **Compliance & Auditing**: Maintain immutable logs of AI outputs, human edits, and cost events for future audits.

## 6. Testing & Validation Strategy
1. **Unit Tests**: Continue maintaining service-level fakes; expand coverage for new caching, retry, and schema handling logic.
2. **Integration Tests**: Exercise FastAPI routes end-to-end with mocked Supabase responses to verify JSON contracts.
3. **Contract Tests**: Snapshot shared Python/TypeScript models to detect drift automatically.
4. **Performance Tests**: Load-test analysis endpoints and UI flows once caching/async processing is introduced.
5. **Resilience Tests**: Simulate OpenAI downtime, Supabase errors, and malformed media to ensure graceful degradation.

## 7. Documentation & Operational Readiness
- Publish runbooks covering OpenAI key rotation, quota monitoring, Supabase incident response, and SmartScope cost controls.
- Update `PROGRESS.md` and public-facing documentation once schema and UI work lands.
- Provide onboarding material for property managers/contractors explaining SmartScope workflows, confidence scores, and feedback expectations.

### 4.6 Cost Monitoring & Operational Controls
- **Cost Persistence**
  - Current: `CostMonitor` constructs payloads but cannot persist because `smartscope_costs` is missing.
  - Required: Create the costs table with indexes/RLS and ensure writes succeed so analytics have real data.
- **Budget Analytics**
  - Current: Budget summaries computed in memory; no API endpoint exposes them.
  - Required: Surface cost telemetry (daily/monthly totals, averages) through dedicated API endpoints.
- **Alerting & Runbooks**
  - Current: Logging-only warnings; no alert integrations or operational documentation.
  - Required: Integrate alert channels (email/Slack/webhook) and publish runbooks covering quota monitoring, fallback handling, and manual escalation paths.

## 5. Non-Functional Requirements
- **Performance**: Analysis requests should complete within 15 seconds P95 once telemetry is in place; UI updates must remain responsive under concurrent usage.
- **Reliability**: Introduce retries/backoff for OpenAI and Supabase interactions, plus monitoring/alerting for failures and budget overruns.
- **Security**: Enforce organization-level access, ensure media URLs are securely fetched, and handle sensitive data per privacy policies.
- **Compliance & Auditing**: Maintain immutable logs of AI outputs, human edits, and cost events for future audits.

## 6. Testing & Validation Strategy
1. **Unit Tests**: Continue maintaining service-level fakes; expand coverage for new caching, retry, and schema handling logic.
2. **Integration Tests**: Exercise FastAPI routes end-to-end with mocked Supabase responses to verify JSON contracts.
3. **Contract Tests**: Snapshot shared Python/TypeScript models to detect drift automatically.
4. **Performance Tests**: Load-test analysis endpoints and UI flows once caching/async processing is introduced.
5. **Resilience Tests**: Simulate OpenAI downtime, Supabase errors, and malformed media to ensure graceful degradation.

## 7. Documentation & Operational Readiness
- Publish runbooks covering OpenAI key rotation, quota monitoring, Supabase incident response, and SmartScope cost controls.
- Update `PROGRESS.md` and public-facing documentation once schema and UI work lands.
- Provide onboarding material for property managers/contractors explaining SmartScope workflows, confidence scores, and feedback expectations.

---
This specification now mirrors the existing FastAPI-based implementation and enumerates the outstanding functionality required to ship SmartScope AI as a production-ready feature.
