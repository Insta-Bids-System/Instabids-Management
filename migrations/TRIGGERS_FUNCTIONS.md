# InstaBids Management - Database Triggers & Functions

**Automated Behaviors and System Functions**

## 🤖 Automatic Behaviors

### Timestamp Management
All tables with `created_at` and `updated_at` columns have automatic timestamp management:

**Tables with Auto-Timestamps:**
- `organizations` - created_at, updated_at
- `user_profiles` - created_at, updated_at  
- `properties` - created_at, updated_at
- `projects` - created_at, updated_at
- `contractors` - created_at, updated_at, joined_at, last_active_at
- `quotes` - created_at, updated_at
- `awards` - created_at, updated_at
- `property_groups` - created_at, updated_at
- `contractor_credentials` - created_at, updated_at
- `contractor_availability` - created_at, updated_at
- `contractor_portfolio` - created_at, updated_at
- `smartscope_analyses` - created_at, updated_at
- `project_questions` - created_at, updated_at

**Behavior:**
- `created_at` set to `NOW()` on INSERT
- `updated_at` set to `NOW()` on INSERT and UPDATE
- Timezone: UTC (TIMESTAMPTZ)

---

## 🔒 Row Level Security (RLS) Functions

### Authentication Helper Functions

#### `auth.uid()`
Returns the UUID of the currently authenticated user
```sql
-- Usage in RLS policies
SELECT * FROM user_profiles WHERE id = auth.uid()
```

#### `auth.role()`  
Returns the current user's role (anon, authenticated, service_role)
```sql
-- Usage for service role access
SELECT * FROM user_profiles WHERE auth.role() = 'service_role'
```

---

## 🔧 Custom Database Functions

### UUID Generation
All tables use `gen_random_uuid()` for primary key generation:
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### Geography/Location Functions
For properties with coordinates:
```sql
-- PostGIS functions available for location queries
ST_DWithin(coordinates, ST_Point(longitude, latitude), radius_meters)
ST_Distance(point1, point2)
```

---

## 📋 Data Validation Rules

### Check Constraints

#### Budget Validation (projects table)
```sql
-- Ensures budget_min <= budget_max
CONSTRAINT budget_check CHECK (budget_min IS NULL OR budget_max IS NULL OR budget_min <= budget_max)
```

#### Amount Validation (quotes table)
```sql
-- Ensures positive amounts
CONSTRAINT total_amount_positive CHECK (total_amount > 0)
CONSTRAINT quantities_positive CHECK (quantity > 0)
```

#### Date Validation (awards table)
```sql
-- Ensures logical date ordering
CONSTRAINT date_order_check CHECK (
    start_date IS NULL OR 
    expected_completion_date IS NULL OR 
    start_date <= expected_completion_date
)
```

#### Rating Validation (contractors table)
```sql
-- Ensures ratings are in valid range
CONSTRAINT rating_range CHECK (rating_average >= 0.00 AND rating_average <= 5.00)
CONSTRAINT rating_count_positive CHECK (rating_count >= 0)
```

---

## 🔄 Cascade Behaviors

### Organization Deletion
When an organization is deleted:
```sql
organizations (DELETE) 
    → user_profiles (CASCADE DELETE)
    → properties (CASCADE DELETE)  
        → projects (CASCADE DELETE)
            → quotes (CASCADE DELETE)
            → awards (CASCADE DELETE)
            → project_media (CASCADE DELETE)
            → invitations (CASCADE DELETE)
            → smartscope_analyses (CASCADE DELETE)
```

### User Profile Deletion  
When a user profile is deleted:
```sql
user_profiles (DELETE)
    → contractors (CASCADE DELETE)
        → quotes (CASCADE DELETE)
        → contractor_credentials (CASCADE DELETE)
        → contractor_availability (CASCADE DELETE)
```

### Property Deletion
When a property is deleted:
```sql
properties (DELETE)
    → projects (CASCADE DELETE)
        → All project-related data (CASCADE DELETE)
```

---

## 📊 Automatic Calculations

### Quote Line Items Total
When inserting/updating quote_line_items:
```sql
-- total_price automatically calculated as quantity * unit_price
total_price = quantity * unit_price
```

### Contractor Rating Updates
When ratings are added (future enhancement):
```sql
-- Update rating_average and rating_count automatically
-- Currently managed by application logic
```

---

## 🗂️ Index Maintenance

### Automatic Index Updates
All indexes are automatically maintained by PostgreSQL:

**Performance Indexes:**
- Primary key indexes (automatic)
- Foreign key indexes (created)
- Unique constraint indexes (automatic)
- Search optimization indexes (created)

**Spatial Indexes:**
- `coordinates` column uses GIST index for geographic queries
- Optimizes location-based contractor search

---

## 🔍 Search Optimization

### Text Search Indexes
For full-text search capabilities:
```sql
-- Properties search
CREATE INDEX IF NOT EXISTS properties_search_idx ON properties 
USING gin(to_tsvector('english', name || ' ' || address || ' ' || city));

-- Projects search  
CREATE INDEX IF NOT EXISTS projects_search_idx ON projects
USING gin(to_tsvector('english', title || ' ' || description));

-- Contractors search
CREATE INDEX IF NOT EXISTS contractors_search_idx ON contractors
USING gin(to_tsvector('english', business_name || ' ' || contact_name));
```

### Array Search Optimization
```sql
-- Contractor specialties search
CREATE INDEX IF NOT EXISTS contractor_specialties_idx ON contractors USING gin(specialties);

-- Service areas search
CREATE INDEX IF NOT EXISTS contractor_service_areas_idx ON contractors USING gin(service_areas);
```

---

## ⚡ Performance Optimizations

### Connection Pooling
Supabase automatically handles connection pooling:
- Max connections: 60 (development tier)
- Pool mode: Transaction pooling
- Timeout: 10 seconds

### Query Optimization
```sql
-- Use prepared statements for repeated queries
-- Leverage RLS for automatic filtering
-- Use indexes for all frequent WHERE clauses
-- Batch inserts when possible
```

---

## 🚨 Error Handling

### Database-Level Constraints
```sql
-- NOT NULL constraints prevent empty required fields
-- UNIQUE constraints prevent duplicates
-- FOREIGN KEY constraints maintain referential integrity
-- CHECK constraints validate data ranges and formats
```

### Supabase Error Codes
```sql
-- 23505: Unique violation
-- 23503: Foreign key violation  
-- 23502: Not null violation
-- 23514: Check constraint violation
```

---

## 🔄 Audit Trail Automation

### Property Changes
All property modifications are automatically logged to `property_audit_log`:
```sql
-- Trigger captures:
-- - What changed (field_name, old_value, new_value)
-- - Who changed it (performed_by)
-- - When it happened (created_at)
-- - Where it came from (ip_address, user_agent)
```

### Authentication Events  
User authentication events logged to `auth_audit_log`:
```sql
-- Automatic logging of:
-- - Login/logout events
-- - Password changes
-- - Profile updates
-- - Failed authentication attempts
```

---

## 🛠️ System Maintenance

### Automatic Cleanup
```sql
-- Expired sessions cleanup (handled by Supabase Auth)
-- Old audit log cleanup (manual/scheduled)
-- Expired invitations (application logic)
-- Soft-deleted properties (manual process)
```

### Statistics Updates
```sql
-- PostgreSQL automatically updates table statistics
-- Query planner uses these for optimization
-- Manual ANALYZE recommended for large data changes
```

---

## 📝 Custom Business Logic

### Quote Versioning
When quotes are updated, previous versions are preserved:
```sql
-- Create new quote record
-- Set previous_version_id to reference old quote
-- Maintain complete audit trail
```

### Project Status Workflow
Status transitions follow business rules:
```sql
draft → open_for_bids → bidding_closed → awarded → in_progress → completed
                                     ↘ cancelled ↙
```

### Contractor Verification Workflow
```sql
pending_review → additional_info_required → verified
                                        ↘ rejected → suspended
```

---

## 🔗 Integration Points

### External System Hooks
Database is ready for external integrations:
- Email notifications (via application)
- Payment processing (via application) 
- Background job queues (via application)
- Analytics tracking (via application)

### API Rate Limiting
Supabase handles API rate limiting automatically:
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour  
- Can be increased with higher tiers

---

**For Agents**: The database handles most automation internally. Your application code should focus on business logic while the database ensures data integrity, security, and basic maintenance automatically.