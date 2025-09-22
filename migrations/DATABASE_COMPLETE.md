# InstaBids Management - COMPLETE Database Reference

**For AI Agents - Everything You Need to Know**

## 🔗 Database Connection Details

```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
Schema Version: 0.0.4
Database: PostgreSQL 15
```

## 🔑 Authentication & API Access

```bash
# Required Environment Variables
SUPABASE_URL=https://lmbpvkfcfhdfaihigfdu.supabase.co  
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxtYnB2a2ZjZmhkZmFpaGlnZmR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY1MTUzNjAsImV4cCI6MjA1MjA5MTM2MH0.gkkLdn-7wQWzY_o0oa9YzYX8QjHShLdJObqJfb3Tnmg

# API Base URLs
REST API: https://lmbpvkfcfhdfaihigfdu.supabase.co/rest/v1/
Auth API: https://lmbpvkfcfhdfaihigfdu.supabase.co/auth/v1/
Storage API: https://lmbpvkfcfhdfaihigfdu.supabase.co/storage/v1/
```

## 📊 Complete Table Inventory

### Core Business Tables (7)
- `organizations` - Multi-tenant organization management
- `user_profiles` - User accounts and authentication  
- `properties` - Property portfolio management
- `projects` - Maintenance work orders and projects
- `contractors` - Service provider network
- `quotes` - Pricing proposals and bids
- `awards` - Accepted work assignments

### Supporting Tables (14)
- `property_groups` - Property grouping and organization
- `property_group_members` - Property-to-group relationships
- `property_audit_log` - Property change tracking
- `project_media` - Project photos and documents
- `contractor_credentials` - Licenses and certifications  
- `contractor_availability` - Service area and schedule
- `contractor_portfolio` - Past work examples
- `quote_line_items` - Detailed quote breakdowns
- `invitations` - Project bidding invitations
- `smartscope_analyses` - AI photo analysis results
- `project_questions` - Custom project fields
- `auth_audit_log` - Security audit trail
- `user_sessions` - Active user sessions
- `password_history` - Password change tracking

**Total Tables: 21**

## 🎯 ALL Enum Types and Values

### business_type
```sql
'sole_proprietor'
'llc' 
'corporation'
'partnership'
```

### property_type
```sql
'single_family'
'multi_family'
'apartment'
'condo'
'townhouse'
'commercial_office'
'commercial_retail'  
'commercial_industrial'
'mixed_use'
'other'
```

### property_status
```sql
'active'
'inactive'
'archived'
```

### project_category
```sql
'plumbing'
'electrical'
'hvac'
'roofing'
'painting'
'landscaping'
'carpentry'
'general_maintenance'
'other'
```

### urgency_level
```sql
'emergency'    -- Immediate response required (< 4 hours)
'urgent'       -- Same day response required
'routine'      -- Standard timeline (1-3 days)  
'scheduled'    -- Planned/scheduled work
```

### project_status
```sql
'draft'           -- Being created
'open_for_bids'   -- Open for bidding
'bidding_closed'  -- No longer accepting bids
'awarded'         -- Contractor selected
'in_progress'     -- Work started
'completed'       -- Work finished
'cancelled'       -- Project cancelled
```

### quote_status
```sql
'received'              -- Initial submission
'processing'            -- Being reviewed
'standardized'          -- Formatted/processed
'needs_clarification'   -- Requires additional info
'updated'               -- Revised/updated
'withdrawn'             -- Contractor withdrew
```

### invitation_status
```sql
'sent'      -- Invitation sent
'viewed'    -- Contractor viewed invitation
'declined'  -- Contractor declined
'accepted'  -- Contractor accepted
'expired'   -- Invitation expired
```

### submission_method
```sql
'pdf'       -- PDF document
'email'     -- Email submission
'photo'     -- Photo-based quote
'web_form'  -- Platform web form
```

### service_area_type
```sql
'zip_codes' -- Specific ZIP codes
'radius'    -- Radius from location
'cities'    -- Specific cities
```

### verification_status
```sql
'pending_review'            -- Under review
'additional_info_required'  -- Needs more info
'verified'                  -- Approved/verified
'rejected'                  -- Rejected
'suspended'                 -- Temporarily suspended
```

## 🔗 Complete Foreign Key Relationships

### organizations
- **Referenced by:**
  - `user_profiles.organization_id` → `organizations.id`
  - `properties.organization_id` → `organizations.id`
  - `property_groups.organization_id` → `organizations.id`

### user_profiles  
- **References:**
  - `user_profiles.organization_id` → `organizations.id`
- **Referenced by:**
  - `contractors.user_id` → `user_profiles.id`
  - `properties.manager_id` → `user_profiles.id`
  - `projects.created_by` → `user_profiles.id`
  - `property_groups.created_by` → `user_profiles.id`
  - `property_group_members.added_by` → `user_profiles.id`
  - `property_audit_log.performed_by` → `user_profiles.id`
  - `project_media.uploaded_by` → `user_profiles.id`
  - `contractor_credentials.verified_by` → `user_profiles.id`
  - `invitations.invited_by` → `user_profiles.id`
  - `project_questions.asked_by` → `user_profiles.id`
  - `project_questions.answered_by` → `user_profiles.id`
  - `awards.awarded_by` → `user_profiles.id`

### properties
- **References:**
  - `properties.organization_id` → `organizations.id`
  - `properties.manager_id` → `user_profiles.id`
- **Referenced by:**
  - `projects.property_id` → `properties.id`
  - `property_group_members.property_id` → `properties.id`
  - `property_audit_log.property_id` → `properties.id`

### projects
- **References:**
  - `projects.property_id` → `properties.id`
  - `projects.created_by` → `user_profiles.id`
- **Referenced by:**
  - `project_media.project_id` → `projects.id`
  - `invitations.project_id` → `projects.id`
  - `quotes.project_id` → `projects.id`
  - `awards.project_id` → `projects.id`
  - `smartscope_analyses.project_id` → `projects.id`
  - `project_questions.project_id` → `projects.id`

### contractors
- **References:**
  - `contractors.user_id` → `user_profiles.id`
- **Referenced by:**
  - `contractor_credentials.contractor_id` → `contractors.id`
  - `contractor_availability.contractor_id` → `contractors.id`
  - `contractor_portfolio.contractor_id` → `contractors.id`
  - `invitations.contractor_id` → `contractors.id`
  - `quotes.contractor_id` → `contractors.id`
  - `awards.contractor_id` → `contractors.id`
  - `project_questions.contractor_id` → `contractors.id`

### quotes
- **References:**
  - `quotes.project_id` → `projects.id`
  - `quotes.contractor_id` → `contractors.id`
  - `quotes.previous_version_id` → `quotes.id` (self-reference)
- **Referenced by:**
  - `quote_line_items.quote_id` → `quotes.id`
  - `awards.quote_id` → `quotes.id`

### property_groups
- **References:**
  - `property_groups.organization_id` → `organizations.id`
  - `property_groups.created_by` → `user_profiles.id`
- **Referenced by:**
  - `property_group_members.group_id` → `property_groups.id`

## 🛡️ Row Level Security (RLS) Policies

**All tables have RLS ENABLED**

### organizations
- **SELECT**: Users can view their organization
  - `id IN (SELECT organization_id FROM user_profiles WHERE id = auth.uid())`
- **UPDATE**: Admins can update their organization  
  - `id IN (SELECT organization_id FROM user_profiles WHERE id = auth.uid() AND user_type = 'property_manager')`

### user_profiles
- **SELECT**: Users can view their own profile
  - `id = auth.uid()`
- **INSERT**: Users can insert their own profile
  - `id = auth.uid()`
- **UPDATE**: Users can update their own profile
  - `id = auth.uid()`
- **ALL**: Service role can access all profiles
  - `auth.role() = 'service_role'`

### properties
- **SELECT**: Users can view properties in their organization
  - `organization_id IN (SELECT organization_id FROM user_profiles WHERE id = auth.uid())`
- **ALL**: Property managers can manage properties
  - `organization_id IN (SELECT organization_id FROM user_profiles WHERE id = auth.uid() AND user_type = 'property_manager')`

### projects
- **SELECT**: Users can view organization projects
  - `property_id IN (SELECT id FROM properties WHERE organization_id IN (SELECT organization_id FROM user_profiles WHERE id = auth.uid()))`
- **INSERT**: Property managers can create projects
  - `property_id IN (SELECT id FROM properties WHERE organization_id IN (SELECT organization_id FROM user_profiles WHERE id = auth.uid() AND user_type IN ('admin', 'manager', 'property_manager')))`

### contractors
- **ALL**: Contractors can view own profile
  - `user_id = auth.uid()`

### quotes
- **ALL**: Contractors can manage own quotes
  - `contractor_id IN (SELECT id FROM contractors WHERE user_id = auth.uid())`

### auth_audit_log
- **SELECT**: Users can view their own audit logs
  - `user_id = auth.uid()`

### user_sessions
- **SELECT**: Users can view their own sessions
  - `user_id = auth.uid()`
- **DELETE**: Users can delete their own sessions
  - `user_id = auth.uid()`

## 📝 Common API Patterns

### Authentication Required Headers
```javascript
headers: {
  'apikey': 'your-anon-key',
  'Authorization': 'Bearer your-jwt-token',
  'Content-Type': 'application/json'
}
```

### Get Organization Properties
```javascript
GET /rest/v1/properties?organization_id=eq.{org_id}&is_deleted=eq.false&order=created_at.desc
```

### Get Active Projects for Property  
```javascript
GET /rest/v1/projects?property_id=eq.{property_id}&status=in.(open_for_bids,in_progress)&order=urgency.desc,created_at.desc
```

### Get Contractor Quotes for Project
```javascript
GET /rest/v1/quotes?project_id=eq.{project_id}&status=eq.standardized&order=total_amount.asc&select=*,contractors(business_name,rating_average)
```

### Create New Project
```javascript
POST /rest/v1/projects
{
  "property_id": "uuid",
  "title": "string", 
  "description": "string",
  "category": "plumbing|electrical|hvac|...",
  "urgency": "emergency|urgent|routine|scheduled",
  "budget_min": 1000.00,
  "budget_max": 5000.00,
  "created_by": "user_uuid"
}
```

## 🗂️ File Organization

This documentation is split into multiple files for agent efficiency:

- `DATABASE_COMPLETE.md` - This overview file
- `TABLES_DETAILED.md` - Every column of every table  
- `API_EXAMPLES.md` - Complete API usage examples
- `RLS_SECURITY.md` - Complete security policy details
- `STORAGE_FILES.md` - File upload and storage patterns

---

**For Agents**: Start here for overview, then reference specific files for detailed implementation.