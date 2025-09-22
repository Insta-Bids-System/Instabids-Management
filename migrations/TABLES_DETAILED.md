# InstaBids Management - COMPLETE Table Schemas

**Every Column, Every Constraint, Every Detail**

## 📋 organizations

**Purpose**: Multi-tenant organization management  
**RLS**: ✅ Enabled - Users see only their organization

```sql
CREATE TABLE organizations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255) NOT NULL,
    type                business_type NOT NULL,
    contact_info        JSONB,
    settings            JSONB,
    billing_info        JSONB,
    subscription_tier   VARCHAR(50) DEFAULT 'free',
    is_active          BOOLEAN DEFAULT true,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `name` for search
- Index on `is_active` for filtering

**Constraints**:
- `name` NOT NULL
- `type` must be valid business_type enum
- `subscription_tier` defaults to 'free'

---

## 👤 user_profiles

**Purpose**: User accounts and authentication  
**RLS**: ✅ Enabled - Users see own profile + organization members

```sql
CREATE TABLE user_profiles (
    id                 UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email              VARCHAR(255) UNIQUE NOT NULL,
    phone              VARCHAR(20),
    full_name          VARCHAR(255),
    user_type          VARCHAR(50) NOT NULL,
    organization_id    UUID REFERENCES organizations(id) ON DELETE CASCADE,
    profile_data       JSONB,
    preferences        JSONB,
    is_active         BOOLEAN DEFAULT true,
    email_verified    BOOLEAN DEFAULT false,
    phone_verified    BOOLEAN DEFAULT false,
    last_login_at     TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `email`
- Index on `organization_id` for joins
- Index on `user_type` for filtering
- Index on `is_active` for filtering

**Constraints**:
- `id` references `auth.users(id)` CASCADE DELETE
- `email` NOT NULL and UNIQUE
- `user_type` NOT NULL
- `organization_id` references `organizations(id)` CASCADE DELETE

**User Types**:
- `admin` - System administrator
- `property_manager` - Property management user
- `manager` - Organization manager
- `user` - Standard user

---

## 🏢 properties

**Purpose**: Property portfolio management with full address and details  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE properties (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                VARCHAR(255),
    address             VARCHAR(500) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(100) NOT NULL,
    zip_code           VARCHAR(20) NOT NULL,
    country            VARCHAR(100) DEFAULT 'United States',
    property_type      property_type NOT NULL,
    property_status    property_status DEFAULT 'active',
    units              INTEGER DEFAULT 1,
    bedrooms           INTEGER,
    bathrooms          DECIMAL(3,1),
    square_feet        INTEGER,
    year_built         INTEGER,
    lot_size          DECIMAL(10,2),
    coordinates        GEOGRAPHY(POINT),
    manager_id         UUID REFERENCES user_profiles(id),
    property_data      JSONB,
    notes              TEXT,
    is_deleted         BOOLEAN DEFAULT false,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `organization_id` for RLS
- Index on `property_type` for filtering
- Index on `property_status` for filtering
- Index on `is_deleted` for filtering
- Spatial index on `coordinates` for location queries
- Index on `zip_code` for location searches
- Index on `manager_id` for assignments

**Constraints**:
- `organization_id` NOT NULL, references `organizations(id)` CASCADE DELETE
- `address` NOT NULL
- `city` NOT NULL  
- `state` NOT NULL
- `zip_code` NOT NULL
- `property_type` must be valid property_type enum
- `property_status` defaults to 'active'
- `units` defaults to 1
- `country` defaults to 'United States'
- `manager_id` references `user_profiles(id)`

---

## 📋 projects

**Purpose**: Maintenance work orders and project management  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE projects (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id         UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    description         TEXT NOT NULL,
    category            project_category NOT NULL,
    urgency            urgency_level NOT NULL,
    status             project_status DEFAULT 'draft',
    budget_min         DECIMAL(10,2),
    budget_max         DECIMAL(10,2),
    timeline           INTERVAL,
    area               VARCHAR(100),
    access_info        TEXT,
    requirements       JSONB,
    completion_notes   TEXT,
    created_by         UUID REFERENCES user_profiles(id),
    completed_at       TIMESTAMPTZ,
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `property_id` for property queries
- Index on `category` for filtering
- Index on `urgency` for prioritization
- Index on `status` for workflow filtering
- Index on `created_by` for user queries
- Index on `created_at` for chronological sorting

**Constraints**:
- `property_id` NOT NULL, references `properties(id)` CASCADE DELETE
- `title` NOT NULL
- `description` NOT NULL
- `category` must be valid project_category enum
- `urgency` must be valid urgency_level enum
- `status` defaults to 'draft'
- `created_by` references `user_profiles(id)`
- `budget_min` <= `budget_max` (check constraint)

---

## 🔧 contractors

**Purpose**: Service provider network and profiles  
**RLS**: ✅ Enabled - Public contractor discovery + private details

```sql
CREATE TABLE contractors (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID UNIQUE REFERENCES user_profiles(id) ON DELETE CASCADE,
    business_name        VARCHAR(255) NOT NULL,
    contact_name         VARCHAR(255) NOT NULL,
    email                VARCHAR(255) UNIQUE NOT NULL,
    phone                VARCHAR(20) NOT NULL,
    business_type        business_type NOT NULL,
    specialties          TEXT[] NOT NULL,
    service_areas        TEXT[] NOT NULL,
    business_address     JSONB,
    verification_status  verification_status DEFAULT 'pending_review',
    rating_average       DECIMAL(3,2) DEFAULT 0.00,
    rating_count         INTEGER DEFAULT 0,
    profile_data         JSONB,
    is_active           BOOLEAN DEFAULT true,
    joined_at           TIMESTAMPTZ DEFAULT NOW(),
    last_active_at      TIMESTAMPTZ DEFAULT NOW(),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `user_id`
- UNIQUE index on `email`
- Index on `specialties` (GIN) for array searches
- Index on `service_areas` (GIN) for location queries
- Index on `verification_status` for filtering
- Index on `rating_average` for ranking
- Index on `is_active` for filtering

**Constraints**:
- `user_id` UNIQUE, references `user_profiles(id)` CASCADE DELETE
- `business_name` NOT NULL
- `contact_name` NOT NULL
- `email` NOT NULL and UNIQUE
- `phone` NOT NULL
- `business_type` must be valid business_type enum
- `specialties` NOT NULL (array)
- `service_areas` NOT NULL (array)
- `verification_status` defaults to 'pending_review'
- `rating_average` defaults to 0.00, range 0.00-5.00
- `rating_count` defaults to 0

---

## 💰 quotes

**Purpose**: Pricing proposals and bid submissions  
**RLS**: ✅ Enabled - Project stakeholders only

```sql
CREATE TABLE quotes (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id       UUID NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    quote_number        VARCHAR(50) UNIQUE NOT NULL,
    total_amount        DECIMAL(10,2) NOT NULL,
    labor_cost          DECIMAL(10,2),
    material_cost       DECIMAL(10,2),
    additional_costs    DECIMAL(10,2),
    timeline_days       INTEGER,
    warranty_period     INTEGER,
    notes               TEXT,
    status              quote_status DEFAULT 'received',
    submission_method   submission_method DEFAULT 'web_form',
    submitted_at        TIMESTAMPTZ,
    expires_at          TIMESTAMPTZ,
    previous_version_id UUID REFERENCES quotes(id),
    metadata            JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `quote_number`
- Index on `project_id` for project queries
- Index on `contractor_id` for contractor queries
- Index on `status` for workflow filtering
- Index on `total_amount` for sorting
- Index on `submitted_at` for chronological sorting
- Index on `previous_version_id` for version tracking

**Constraints**:
- `project_id` NOT NULL, references `projects(id)` CASCADE DELETE
- `contractor_id` NOT NULL, references `contractors(id)` CASCADE DELETE
- `quote_number` NOT NULL and UNIQUE
- `total_amount` NOT NULL and > 0
- `status` defaults to 'received'
- `submission_method` defaults to 'web_form'
- `previous_version_id` references `quotes(id)` for versioning
- `timeline_days` > 0 if specified
- `warranty_period` >= 0 if specified

---

## 🏆 awards

**Purpose**: Accepted work assignments  
**RLS**: ✅ Enabled - Project stakeholders only

```sql
CREATE TABLE awards (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id   UUID NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    quote_id        UUID REFERENCES quotes(id),
    awarded_by      UUID REFERENCES user_profiles(id),
    award_amount    DECIMAL(10,2) NOT NULL,
    award_notes     TEXT,
    start_date      DATE,
    expected_completion_date DATE,
    actual_completion_date DATE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `project_id` for project queries
- Index on `contractor_id` for contractor queries
- Index on `quote_id` for quote references
- Index on `awarded_by` for user queries
- Index on `start_date` for scheduling

**Constraints**:
- `project_id` NOT NULL, references `projects(id)` CASCADE DELETE
- `contractor_id` NOT NULL, references `contractors(id)` CASCADE DELETE
- `quote_id` references `quotes(id)`
- `awarded_by` references `user_profiles(id)`
- `award_amount` NOT NULL and > 0
- `start_date` <= `expected_completion_date` if both specified
- `expected_completion_date` <= `actual_completion_date` if both specified

---

## 📁 property_groups

**Purpose**: Property grouping and organization  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE property_groups (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    color_code      VARCHAR(7),
    created_by      UUID REFERENCES user_profiles(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `organization_id` for RLS
- Index on `name` for searching
- Index on `created_by` for user queries

**Constraints**:
- `organization_id` NOT NULL, references `organizations(id)` CASCADE DELETE
- `name` NOT NULL
- `created_by` references `user_profiles(id)`
- `color_code` format '#RRGGBB' if specified

---

## 🔗 property_group_members

**Purpose**: Property-to-group relationships (many-to-many)  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE property_group_members (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id    UUID NOT NULL REFERENCES property_groups(id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    added_by    UUID REFERENCES user_profiles(id),
    added_at    TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(group_id, property_id)
);
```

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `(group_id, property_id)`
- Index on `group_id` for group queries
- Index on `property_id` for property queries
- Index on `added_by` for user queries

**Constraints**:
- `group_id` NOT NULL, references `property_groups(id)` CASCADE DELETE
- `property_id` NOT NULL, references `properties(id)` CASCADE DELETE
- `added_by` references `user_profiles(id)`
- UNIQUE constraint on `(group_id, property_id)` - no duplicates

---

## 📝 property_audit_log

**Purpose**: Property change tracking and audit trail  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE property_audit_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id   UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    action        VARCHAR(50) NOT NULL,
    field_name    VARCHAR(100),
    old_value     TEXT,
    new_value     TEXT,
    performed_by  UUID REFERENCES user_profiles(id),
    ip_address    INET,
    user_agent    TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `property_id` for property history
- Index on `action` for filtering
- Index on `performed_by` for user queries
- Index on `created_at` for chronological sorting

**Constraints**:
- `property_id` NOT NULL, references `properties(id)` CASCADE DELETE
- `action` NOT NULL (CREATE, UPDATE, DELETE, etc.)
- `performed_by` references `user_profiles(id)`

---

## 📷 project_media

**Purpose**: Project photos and documents  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE project_media (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id   UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    file_name    VARCHAR(500) NOT NULL,
    file_path    VARCHAR(1000) NOT NULL,
    file_type    VARCHAR(100) NOT NULL,
    file_size    BIGINT,
    media_type   VARCHAR(50) NOT NULL,
    description  TEXT,
    uploaded_by  UUID REFERENCES user_profiles(id),
    uploaded_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `project_id` for project queries
- Index on `media_type` for filtering
- Index on `uploaded_by` for user queries
- Index on `uploaded_at` for chronological sorting

**Constraints**:
- `project_id` NOT NULL, references `projects(id)` CASCADE DELETE
- `file_name` NOT NULL
- `file_path` NOT NULL
- `file_type` NOT NULL (extension: .jpg, .pdf, etc.)
- `media_type` NOT NULL (photo, document, video, etc.)
- `uploaded_by` references `user_profiles(id)`
- `file_size` > 0 if specified

---

## 📜 contractor_credentials

**Purpose**: Licenses and certifications  
**RLS**: ✅ Enabled - Contractor and organization access

```sql
CREATE TABLE contractor_credentials (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contractor_id     UUID NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    credential_type   VARCHAR(100) NOT NULL,
    credential_name   VARCHAR(255) NOT NULL,
    issuing_authority VARCHAR(255),
    credential_number VARCHAR(100),
    issue_date        DATE,
    expiration_date   DATE,
    verification_status verification_status DEFAULT 'pending_review',
    verified_by       UUID REFERENCES user_profiles(id),
    verified_at       TIMESTAMPTZ,
    document_path     VARCHAR(1000),
    notes             TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `contractor_id` for contractor queries
- Index on `credential_type` for filtering
- Index on `verification_status` for workflow
- Index on `expiration_date` for expiration tracking
- Index on `verified_by` for user queries

**Constraints**:
- `contractor_id` NOT NULL, references `contractors(id)` CASCADE DELETE
- `credential_type` NOT NULL (license, certification, insurance, etc.)
- `credential_name` NOT NULL
- `verification_status` defaults to 'pending_review'
- `verified_by` references `user_profiles(id)`
- `issue_date` <= `expiration_date` if both specified

---

## 🗓️ contractor_availability

**Purpose**: Service area and schedule availability  
**RLS**: ✅ Enabled - Contractor access

```sql
CREATE TABLE contractor_availability (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contractor_id     UUID NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    service_area_type service_area_type NOT NULL,
    service_areas     TEXT[] NOT NULL,
    radius_miles      INTEGER,
    base_location     GEOGRAPHY(POINT),
    availability_notes TEXT,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `contractor_id` for contractor queries
- Index on `service_area_type` for filtering
- Index on `service_areas` (GIN) for area searches
- Spatial index on `base_location` for location queries

**Constraints**:
- `contractor_id` NOT NULL, references `contractors(id)` CASCADE DELETE
- `service_area_type` must be valid service_area_type enum
- `service_areas` NOT NULL (array of ZIP codes, cities, etc.)
- `radius_miles` > 0 if service_area_type is 'radius'

---

## 🏗️ contractor_portfolio

**Purpose**: Past work examples and project showcase  
**RLS**: ✅ Enabled - Public display + contractor management

```sql
CREATE TABLE contractor_portfolio (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contractor_id    UUID NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    project_title    VARCHAR(255) NOT NULL,
    project_description TEXT,
    completion_date  DATE,
    project_value    DECIMAL(10,2),
    client_name      VARCHAR(255),
    location         VARCHAR(255),
    photos           TEXT[],
    testimonial      TEXT,
    display_order    INTEGER DEFAULT 0,
    is_featured      BOOLEAN DEFAULT false,
    is_public        BOOLEAN DEFAULT true,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `contractor_id` for contractor queries
- Index on `display_order` for sorting
- Index on `is_featured` for featured content
- Index on `is_public` for public display
- Index on `completion_date` for chronological sorting

**Constraints**:
- `contractor_id` NOT NULL, references `contractors(id)` CASCADE DELETE
- `project_title` NOT NULL
- `project_value` >= 0 if specified
- `display_order` defaults to 0
- `is_featured` defaults to false
- `is_public` defaults to true

---

## 💬 quote_line_items

**Purpose**: Detailed quote breakdowns (line items)  
**RLS**: ✅ Enabled - Quote stakeholders only

```sql
CREATE TABLE quote_line_items (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_id     UUID NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    description  TEXT NOT NULL,
    quantity     DECIMAL(10,2) NOT NULL DEFAULT 1.0,
    unit_price   DECIMAL(10,2) NOT NULL,
    total_price  DECIMAL(10,2) NOT NULL,
    category     VARCHAR(100),
    notes        TEXT,
    line_order   INTEGER DEFAULT 0,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `quote_id` for quote queries
- Index on `category` for grouping
- Index on `line_order` for sorting

**Constraints**:
- `quote_id` NOT NULL, references `quotes(id)` CASCADE DELETE
- `description` NOT NULL
- `quantity` NOT NULL, > 0
- `unit_price` NOT NULL, >= 0
- `total_price` NOT NULL, >= 0
- `total_price` = `quantity` * `unit_price` (check constraint)
- `line_order` defaults to 0

---

## 📨 invitations

**Purpose**: Project bidding invitations  
**RLS**: ✅ Enabled - Project stakeholders only

```sql
CREATE TABLE invitations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID NOT NULL REFERENCES contractors(id) ON DELETE CASCADE,
    invited_by    UUID REFERENCES user_profiles(id),
    status        invitation_status DEFAULT 'sent',
    message       TEXT,
    invited_at    TIMESTAMPTZ DEFAULT NOW(),
    viewed_at     TIMESTAMPTZ,
    responded_at  TIMESTAMPTZ,
    expires_at    TIMESTAMPTZ,
    
    UNIQUE(project_id, contractor_id)
);
```

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `(project_id, contractor_id)`
- Index on `project_id` for project queries
- Index on `contractor_id` for contractor queries
- Index on `status` for workflow filtering
- Index on `invited_by` for user queries
- Index on `expires_at` for expiration checks

**Constraints**:
- `project_id` NOT NULL, references `projects(id)` CASCADE DELETE
- `contractor_id` NOT NULL, references `contractors(id)` CASCADE DELETE
- `invited_by` references `user_profiles(id)`
- `status` defaults to 'sent'
- UNIQUE constraint on `(project_id, contractor_id)` - no duplicate invitations
- `viewed_at` >= `invited_at` if specified
- `responded_at` >= `viewed_at` if specified

---

## 🤖 smartscope_analyses

**Purpose**: AI-powered photo analysis for maintenance issues  
**RLS**: ✅ Enabled - Organization-scoped access

```sql
CREATE TABLE smartscope_analyses (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id              UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    photo_urls              TEXT[] NOT NULL,
    primary_issue           TEXT NOT NULL,
    severity                VARCHAR(50) NOT NULL,
    category                VARCHAR(100) NOT NULL,
    estimated_hours         DECIMAL(5,2),
    safety_notes            TEXT,
    confidence_score        DECIMAL(3,2) NOT NULL,
    openai_response_raw     JSONB NOT NULL,
    additional_observations TEXT[],
    metadata                JSONB,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `project_id` for project queries
- Index on `category` for filtering
- Index on `severity` for prioritization
- Index on `confidence_score` for quality filtering
- Index on `created_at` for chronological sorting

**Constraints**:
- `project_id` NOT NULL, references `projects(id)` CASCADE DELETE
- `photo_urls` NOT NULL (array of image URLs)
- `primary_issue` NOT NULL
- `severity` NOT NULL (low, medium, high, critical)
- `category` NOT NULL (matches project categories)
- `confidence_score` NOT NULL, range 0.00-1.00
- `openai_response_raw` NOT NULL (full AI response)
- `estimated_hours` >= 0 if specified

---

## ❓ project_questions

**Purpose**: Custom project fields and Q&A  
**RLS**: ✅ Enabled - Project stakeholders only

```sql
CREATE TABLE project_questions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    contractor_id UUID REFERENCES contractors(id) ON DELETE CASCADE,
    question      TEXT NOT NULL,
    answer        TEXT,
    asked_by      UUID REFERENCES user_profiles(id),
    answered_by   UUID REFERENCES user_profiles(id),
    question_type VARCHAR(50) DEFAULT 'text',
    is_required   BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    asked_at      TIMESTAMPTZ DEFAULT NOW(),
    answered_at   TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `project_id` for project queries
- Index on `contractor_id` for contractor queries
- Index on `asked_by` for user queries
- Index on `answered_by` for user queries
- Index on `display_order` for sorting
- Index on `is_required` for validation

**Constraints**:
- `project_id` NOT NULL, references `projects(id)` CASCADE DELETE
- `contractor_id` references `contractors(id)` CASCADE DELETE (optional)
- `question` NOT NULL
- `asked_by` references `user_profiles(id)`
- `answered_by` references `user_profiles(id)`
- `question_type` defaults to 'text' (text, number, date, choice, etc.)
- `is_required` defaults to false
- `display_order` defaults to 0
- `answered_at` >= `asked_at` if both specified

---

## 🔒 auth_audit_log

**Purpose**: Security audit trail  
**RLS**: ✅ Enabled - Users see only their own logs

```sql
CREATE TABLE auth_audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    action      VARCHAR(100) NOT NULL,
    details     JSONB,
    ip_address  INET,
    user_agent  TEXT,
    success     BOOLEAN NOT NULL,
    error_message TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `user_id` for user queries
- Index on `action` for filtering
- Index on `success` for filtering
- Index on `created_at` for chronological sorting
- Index on `ip_address` for security analysis

**Constraints**:
- `user_id` references `user_profiles(id)` CASCADE DELETE
- `action` NOT NULL (LOGIN, LOGOUT, PASSWORD_CHANGE, etc.)
- `success` NOT NULL

---

## 💻 user_sessions

**Purpose**: Active user sessions  
**RLS**: ✅ Enabled - Users see only their own sessions

```sql
CREATE TABLE user_sessions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address   INET,
    user_agent   TEXT,
    expires_at   TIMESTAMPTZ NOT NULL,
    is_active    BOOLEAN DEFAULT true,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `session_token`
- Index on `user_id` for user queries
- Index on `expires_at` for cleanup
- Index on `is_active` for filtering
- Index on `last_accessed_at` for activity tracking

**Constraints**:
- `user_id` NOT NULL, references `user_profiles(id)` CASCADE DELETE
- `session_token` NOT NULL and UNIQUE
- `expires_at` NOT NULL
- `is_active` defaults to true
- `expires_at` > `created_at`

---

## 🔐 password_history

**Purpose**: Password change tracking (prevent reuse)  
**RLS**: ✅ Enabled - Users see only their own history

```sql
CREATE TABLE password_history (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes**:
- PRIMARY KEY on `id`
- Index on `user_id` for user queries
- Index on `created_at` for chronological sorting

**Constraints**:
- `user_id` NOT NULL, references `user_profiles(id)` CASCADE DELETE
- `password_hash` NOT NULL (bcrypt or similar)

---

## 📊 Summary Statistics

- **Total Tables**: 21
- **Total Columns**: ~200 columns across all tables
- **Total Indexes**: ~80 indexes for performance
- **Total Foreign Keys**: 35 relationships
- **Total Enums**: 11 custom types with 70+ values
- **RLS Enabled**: All 21 tables have Row Level Security

**For Agents**: Every column, constraint, and relationship is documented above. Use this as your complete reference for database operations.