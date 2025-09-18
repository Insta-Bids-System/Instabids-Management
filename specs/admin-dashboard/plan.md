# Technical Implementation Plan: Admin Dashboard

## Overview
Comprehensive analytics and monitoring dashboard for InstaBids platform administrators to track system performance, user engagement, and business metrics.

## Technical Architecture

### System Design
```
┌─────────────────────────────────────────────────────┐
│                  Admin Dashboard UI                  │
│  (React + Chart.js/D3.js + Real-time WebSocket)     │
└────────────────┬───────────────────────┬────────────┘
                 │                       │
    ┌────────────▼──────────┐  ┌────────▼──────────┐
    │    Analytics API      │  │   Real-time Feed   │
    │  (FastAPI Endpoints)  │  │    (WebSocket)     │
    └────────────┬──────────┘  └────────┬──────────┘
                 │                       │
    ┌────────────▼───────────────────────▼────────────┐
    │           Supabase Database                     │
    │  (Read-only queries + Materialized views)       │
    └──────────────────────────────────────────────────┘
```

### Technology Stack
- **Frontend**: React with TypeScript
- **Charts**: Chart.js for simple charts, D3.js for complex visualizations
- **Backend**: FastAPI read-only analytics endpoints
- **Database**: Supabase PostgreSQL with materialized views for performance
- **Real-time**: WebSocket connections for live metrics
- **Caching**: Redis for expensive aggregation caching
- **Export**: PDF generation with Puppeteer, CSV with native libraries

## Core Components

### 1. Dashboard Layout System
```typescript
interface DashboardLayout {
  header: MetricsBar;        // Key KPIs
  sidebar: Navigation;       // Section navigation
  main: {
    overview: SystemMetrics;
    projects: ProjectAnalytics;
    contractors: ContractorMetrics;
    quotes: QuoteAnalytics;
    ai: SmartScopePerformance;
    audit: AdminActivityLog;
  };
}
```

### 2. Analytics Engine
```python
class AnalyticsService:
    def get_system_metrics() -> SystemMetrics
    def get_project_analytics(filters) -> ProjectData
    def get_contractor_performance() -> ContractorMetrics
    def get_quote_conversion_rates() -> QuoteAnalytics
    def get_ai_performance() -> AIMetrics
    def generate_report(type, format) -> Report
```

### 3. Real-time Metrics Stream
```typescript
interface MetricsWebSocket {
  activeUsers: number;
  openProjects: number;
  pendingQuotes: number;
  processingJobs: number;
  systemHealth: HealthStatus;
}
```

## Database Schema

### Analytics Tables (Read-only Views)
```sql
-- Materialized view for dashboard metrics
CREATE MATERIALIZED VIEW dashboard_metrics AS
SELECT 
  COUNT(DISTINCT u.id) as total_users,
  COUNT(DISTINCT p.id) as total_projects,
  COUNT(DISTINCT c.id) as verified_contractors,
  COUNT(DISTINCT q.id) as total_quotes,
  AVG(q.confidence_score) as avg_quote_confidence,
  AVG(s.overall_confidence) as avg_ai_confidence
FROM user_profiles u
LEFT JOIN projects p ON p.created_by = u.id
LEFT JOIN contractors c ON c.user_id = u.id
LEFT JOIN quotes q ON q.project_id = p.id
LEFT JOIN smartscope_analyses s ON s.project_id = p.id;

-- Admin audit log table
CREATE TABLE admin_audit_log (
  id UUID PRIMARY KEY,
  admin_id UUID REFERENCES user_profiles(id),
  action_type VARCHAR(50),
  target_entity VARCHAR(50),
  target_id UUID,
  change_details JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## API Endpoints

### Analytics Endpoints
```
GET /api/admin/dashboard
  → Returns complete dashboard data

GET /api/admin/metrics/system
  → System-wide metrics and health status

GET /api/admin/metrics/projects?range={7d|30d|90d}
  → Project creation and completion metrics

GET /api/admin/metrics/contractors?sort={revenue|rating|success_rate}
  → Contractor performance rankings

GET /api/admin/metrics/quotes?group_by={method|status|confidence}
  → Quote submission and conversion analytics

GET /api/admin/metrics/ai?metric={accuracy|confidence|processing_time}
  → SmartScope AI performance metrics

GET /api/admin/reports/export?format={csv|pdf}&type={summary|detailed}
  → Export dashboard data

POST /api/admin/actions/{action_type}
  → Log admin actions (suspend user, modify project, etc.)

GET /api/admin/audit-log?filter={user|action|date_range}
  → Retrieve audit trail
```

## Security & Performance

### Access Control
```python
# Role-based permissions
class AdminRole(Enum):
    SUPER_ADMIN = "super_admin"  # Full access
    ADMIN = "admin"              # Modify access
    VIEWER = "viewer"            # Read-only

# Decorator for endpoint protection
@require_admin_role([AdminRole.SUPER_ADMIN, AdminRole.ADMIN])
def modify_user_status(user_id: UUID, status: str):
    # Implementation
```

### Performance Optimization
- **Materialized Views**: Pre-compute expensive aggregations
- **Redis Caching**: Cache dashboard data for 30 seconds
- **Query Optimization**: Use indexes on commonly filtered columns
- **Pagination**: Limit result sets for large data queries
- **Lazy Loading**: Load detailed metrics on demand

## Implementation Phases

### Phase 1: Core Dashboard (2 days)
- Basic layout and navigation
- System metrics display
- User and project counts
- Simple chart implementations

### Phase 2: Analytics Engine (2 days)
- Project analytics
- Contractor performance metrics
- Quote conversion tracking
- Export functionality

### Phase 3: Real-time Features (1 day)
- WebSocket connection for live metrics
- Auto-refresh mechanism
- Activity feed
- System health monitoring

### Phase 4: Advanced Features (2 days)
- AI performance tracking
- Contractor verification queue
- Admin action logging
- Audit trail interface

### Phase 5: Polish & Testing (1 day)
- Responsive design
- Performance optimization
- Security hardening
- End-to-end testing

## Testing Strategy

### Unit Tests
- Analytics calculation accuracy
- Data aggregation functions
- Permission checks
- Export formatting

### Integration Tests
- API endpoint responses
- Database query performance
- WebSocket connections
- Cache invalidation

### Performance Tests
- Dashboard load time < 2 seconds
- Real-time updates < 100ms latency
- Export generation < 10 seconds
- Support 100+ concurrent admin users

## Monitoring & Alerts

### Key Metrics to Track
- Dashboard load times
- Query execution times
- Cache hit rates
- WebSocket connection stability
- Export success rates

### Alert Thresholds
- Query time > 5 seconds
- Cache miss rate > 50%
- WebSocket disconnection rate > 10%
- Failed exports > 5%

## Dependencies

### External Services
- Redis for caching
- WebSocket server for real-time updates
- PDF generation service (Puppeteer)

### Internal Dependencies
- All database tables (read-only access)
- Authentication system for admin verification
- Existing API infrastructure

## Success Criteria

- ✅ Dashboard loads in < 2 seconds
- ✅ All metrics update every 30 seconds
- ✅ Export functionality works for CSV and PDF
- ✅ Role-based access control enforced
- ✅ Audit trail captures all admin actions
- ✅ Mobile responsive design
- ✅ 99.9% uptime for dashboard availability