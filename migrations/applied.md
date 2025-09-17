# Database Migrations Tracker

## 🗄️ Supabase Connection
```yaml
Status: CONNECTED
Project: lmbpvkfcfhdfaihigfdu
Environment: Development
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
```

## 📊 Applied Migrations

### ⏳ Pending (Not Applied)
```sql
-- 003_projects_and_contractors.sql
-- Creates: projects, contractors, invitations tables
-- Status: NOT APPLIED

-- 004_quotes_and_messaging.sql
-- Creates: quotes, messages, awards tables
-- Status: NOT APPLIED

-- 005_ai_and_memory.sql
-- Creates: property_memory, ai_agent_logs tables
-- Status: NOT APPLIED
```

### ✅ Applied Migrations

#### 001_initial_schema.sql
- **Applied**: 2025-01-17 17:15:00 UTC
- **Tables Created**: organizations, user_profiles, properties
- **Indexes**: 4 indexes for performance
- **RLS Policies**: Full security policies enabled
- **Status**: ✅ SUCCESS

#### 002_auth_extensions.sql
- **Applied**: 2025-01-17 18:45:00 UTC
- **Tables Created**: auth_audit_log, user_sessions, password_history
- **Indexes**: 9 indexes for performance
- **RLS Policies**: User-scoped policies
- **Status**: ✅ SUCCESS

## 📝 How to Apply Migrations

### Method 1: Using Supabase MCP Tools
```python
# In chat, use:
mcp__supabase__apply_migration(
    project_id="[your-project-id]",
    name="001_initial_schema",
    query="[SQL from migrations folder]"
)
```

### Method 2: Using Supabase CLI
```bash
# Create migration
supabase migration new initial_schema

# Copy SQL from docs/DATABASE_SCHEMA.md
# Then push
supabase db push
```

### Method 3: Supabase Dashboard
1. Go to SQL Editor
2. Paste migration SQL
3. Run
4. Update this file

## 🔄 Migration Files

### 001_initial_schema.sql
```sql
-- Organizations & Users
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    full_name VARCHAR(255),
    user_type VARCHAR(50) NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    address JSONB NOT NULL,
    property_type VARCHAR(50),
    units INTEGER DEFAULT 1,
    year_built INTEGER,
    square_feet INTEGER,
    property_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 002_projects_and_contractors.sql
```sql
-- Will create: projects, contractors, invitations tables
-- Status: NOT CREATED
```

### 003_quotes_and_messaging.sql
```sql
-- Will create: quotes, messages, awards tables  
-- Status: NOT CREATED
```

### 004_ai_and_memory.sql
```sql
-- Will create: property_memory, ai_agent_logs tables
-- Status: NOT CREATED
```

## ⚠️ Important Rules

1. **NEVER** run migrations without backing up first
2. **ALWAYS** test in development first
3. **MUST** update this file after applying
4. **KEEP** migrations small and focused
5. **NUMBER** sequentially (001, 002, etc.)

## 🔍 How to Check Current State

```sql
-- Run this in Supabase to see what exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

## 📅 Migration History

| Date | Migration | Applied By | Notes |
|------|-----------|------------|-------|
| 2025-01-17 | 001_initial_schema | Claude | Organizations, users, properties tables with RLS |
| 2025-01-17 | 002_auth_extensions | Claude | Audit logs, sessions, password history tables |

---
Last Updated: 2025-01-17 18:45 UTC
Total Migrations: 2 applied, 3 pending