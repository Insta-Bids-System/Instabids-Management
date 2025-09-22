# InstaBids Management - Database Reference

**For AI Agents and External Services**

## 🗄️ Database Connection
```yaml
Project: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
Schema Version: 0.0.4
Total Tables: 21
Last Updated: 2025-01-17 21:15 UTC
```

## 📊 Table Overview

### Core Business Tables (7)
- `organizations` - Multi-tenant organization management
- `user_profiles` - User accounts and profiles
- `properties` - Property portfolio management
- `projects` - Maintenance projects and work orders
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

## 🔗 Core Relationships

```
organizations
├── user_profiles (1:many)
├── properties (1:many)
└── projects (1:many)

properties
├── projects (1:many)
├── property_groups (many:many via property_group_members)
└── property_audit_log (1:many)

projects
├── project_media (1:many)
├── invitations (1:many)
├── quotes (1:many)
├── awards (1:many)
├── smartscope_analyses (1:many)
└── project_questions (1:many)

contractors
├── contractor_credentials (1:many)
├── contractor_availability (1:many)
├── contractor_portfolio (1:many)
├── invitations (1:many)
└── quotes (1:many)

quotes
├── quote_line_items (1:many)
└── awards (1:many)
```

## 📋 Table Schemas

### organizations
**Purpose**: Multi-tenant organization management
```sql
id                  UUID PRIMARY KEY
name               VARCHAR(255) NOT NULL
type               business_type_enum NOT NULL
contact_info       JSONB
settings           JSONB
billing_info       JSONB
subscription_tier  VARCHAR(50) DEFAULT 'free'
is_active          BOOLEAN DEFAULT true
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Users see only their organization

### user_profiles  
**Purpose**: User accounts and authentication
```sql
id                 UUID PRIMARY KEY
email              VARCHAR(255) UNIQUE NOT NULL
phone              VARCHAR(20)
full_name          VARCHAR(255)
role               user_role_enum NOT NULL
organization_id    UUID REFERENCES organizations(id)
profile_data       JSONB
preferences        JSONB
is_active          BOOLEAN DEFAULT true
email_verified     BOOLEAN DEFAULT false
phone_verified     BOOLEAN DEFAULT false
last_login_at      TIMESTAMPTZ
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Users see own profile + organization members

### properties
**Purpose**: Property portfolio management with full address and details
```sql
id                 UUID PRIMARY KEY
organization_id    UUID REFERENCES organizations(id) NOT NULL
name               VARCHAR(255)
address            VARCHAR(500) NOT NULL
city               VARCHAR(100) NOT NULL
state              VARCHAR(100) NOT NULL
zip_code           VARCHAR(20) NOT NULL
country            VARCHAR(100) DEFAULT 'United States'
property_type      property_type_enum NOT NULL
property_status    property_status_enum DEFAULT 'active'
units              INTEGER DEFAULT 1
bedrooms           INTEGER
bathrooms          DECIMAL(3,1)
square_feet        INTEGER
year_built         INTEGER
lot_size           DECIMAL(10,2)
coordinates        GEOGRAPHY(POINT)
property_data      JSONB
notes              TEXT
is_deleted         BOOLEAN DEFAULT false
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Organization-scoped access

### projects
**Purpose**: Maintenance work orders and project management
```sql
id                 UUID PRIMARY KEY
organization_id    UUID REFERENCES organizations(id) NOT NULL
property_id        UUID REFERENCES properties(id) NOT NULL
title              VARCHAR(255) NOT NULL
description        TEXT NOT NULL
category           project_category_enum NOT NULL
urgency            urgency_level_enum NOT NULL
status             project_status_enum DEFAULT 'draft'
budget_min         DECIMAL(10,2)
budget_max         DECIMAL(10,2)
timeline           INTERVAL
area               VARCHAR(100)
access_info        TEXT
requirements       JSONB
completion_notes   TEXT
created_by         UUID REFERENCES user_profiles(id)
assigned_to        UUID REFERENCES contractors(id)
completed_at       TIMESTAMPTZ
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Organization-scoped access

### contractors
**Purpose**: Service provider network and profiles
```sql
id                 UUID PRIMARY KEY
business_name      VARCHAR(255) NOT NULL
contact_name       VARCHAR(255) NOT NULL
email              VARCHAR(255) UNIQUE NOT NULL
phone              VARCHAR(20) NOT NULL
business_type      business_type_enum NOT NULL
specialties        TEXT[] NOT NULL
service_areas      TEXT[] NOT NULL
business_address   JSONB
verification_status verification_status_enum DEFAULT 'pending'
rating_average     DECIMAL(3,2) DEFAULT 0.00
rating_count       INTEGER DEFAULT 0
profile_data       JSONB
is_active          BOOLEAN DEFAULT true
joined_at          TIMESTAMPTZ DEFAULT NOW()
last_active_at     TIMESTAMPTZ DEFAULT NOW()
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Public contractor discovery + private details

### quotes
**Purpose**: Pricing proposals and bid submissions  
```sql
id                 UUID PRIMARY KEY
project_id         UUID REFERENCES projects(id) NOT NULL
contractor_id      UUID REFERENCES contractors(id) NOT NULL
invitation_id      UUID REFERENCES invitations(id)
quote_number       VARCHAR(50) UNIQUE NOT NULL
total_amount       DECIMAL(10,2) NOT NULL
labor_cost         DECIMAL(10,2)
material_cost      DECIMAL(10,2)
additional_costs   DECIMAL(10,2)
timeline_days      INTEGER
warranty_period    INTEGER
notes              TEXT
status             quote_status_enum DEFAULT 'draft'
submission_method  submission_method_enum DEFAULT 'platform'
submitted_at       TIMESTAMPTZ
expires_at         TIMESTAMPTZ
metadata           JSONB
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Project stakeholders only

### smartscope_analyses
**Purpose**: AI-powered photo analysis for maintenance issues
```sql
id                 UUID PRIMARY KEY
project_id         UUID REFERENCES projects(id) NOT NULL
photo_urls         TEXT[] NOT NULL
primary_issue      TEXT NOT NULL
severity           VARCHAR(50) NOT NULL
category           VARCHAR(100) NOT NULL
estimated_hours    DECIMAL(5,2)
safety_notes       TEXT
confidence_score   DECIMAL(3,2) NOT NULL
openai_response_raw JSONB NOT NULL
additional_observations TEXT[]
metadata           JSONB
created_at         TIMESTAMPTZ DEFAULT NOW()
updated_at         TIMESTAMPTZ DEFAULT NOW()
```
**RLS**: Enabled - Organization-scoped access

## 🎯 Enum Types

### business_type_enum
```sql
'property_management'
'real_estate'
'construction'
'maintenance'
'consulting'
'other'
```

### property_type_enum  
```sql
'single_family'
'multi_family'
'condo'
'townhouse'
'commercial'
'industrial'
'mixed_use'
'land'
```

### project_category_enum
```sql
'plumbing'
'electrical'
'hvac'
'roofing'
'flooring'
'painting'
'landscaping'
'cleaning'
'appliance_repair'
'structural'
'pest_control'
'security'
'other'
```

### urgency_level_enum
```sql
'emergency'    -- Immediate response required (< 4 hours)
'urgent'       -- Same day response required  
'normal'       -- Standard timeline (1-3 days)
'low'          -- Flexible timeline (1+ weeks)
```

### project_status_enum
```sql
'draft'        -- Being created
'published'    -- Open for bidding
'in_progress'  -- Work started
'completed'    -- Work finished
'cancelled'    -- Project cancelled
'on_hold'      -- Temporarily paused
```

## 🔍 Common Query Patterns

### Get Organization Properties
```sql
SELECT * FROM properties 
WHERE organization_id = $1 
AND is_deleted = false
ORDER BY created_at DESC;
```

### Get Active Projects for Property
```sql
SELECT p.*, prop.address, prop.name as property_name
FROM projects p
JOIN properties prop ON p.property_id = prop.id
WHERE p.property_id = $1 
AND p.status IN ('published', 'in_progress')
ORDER BY p.urgency DESC, p.created_at DESC;
```

### Get Contractor Quotes for Project
```sql
SELECT q.*, c.business_name, c.rating_average
FROM quotes q
JOIN contractors c ON q.contractor_id = c.id
WHERE q.project_id = $1
AND q.status = 'submitted'
ORDER BY q.total_amount ASC;
```

### Get SmartScope Analysis Results
```sql
SELECT sa.*, p.title as project_title
FROM smartscope_analyses sa
JOIN projects p ON sa.project_id = p.id
WHERE p.organization_id = $1
ORDER BY sa.created_at DESC
LIMIT 10;
```

## 🛡️ Security & RLS

**All tables have Row Level Security (RLS) enabled** with organization-scoped policies:

- **Organizations**: Users access only their organization
- **Properties/Projects**: Organization members only
- **Contractors**: Public discovery + private profile details
- **Quotes/Awards**: Project stakeholders only
- **Audit Logs**: Organization admins only

## 📝 Migration Status

**Applied Migrations:**
- ✅ 001_initial_schema.sql (Organizations, users, properties)
- ✅ 002_auth_extensions.sql (Auth audit, sessions, password history)  
- ✅ 003_property_management.sql (Property groups, audit logs, geocoding)
- ✅ 004_marketplace_core.sql (Projects, contractors, quotes, SmartScope AI)

**Total Tables**: 21 tables across 4 migration files

---

**For Agents**: Use this reference to understand table structure, relationships, and query patterns. All data access respects RLS policies based on organization membership.