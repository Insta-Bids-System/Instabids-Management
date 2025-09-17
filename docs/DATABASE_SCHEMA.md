# Supabase Database Schema

## 🗄️ Core Tables Structure

```sql
-- Organizations & Users
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'landlord', 'hoa', 'str', 'pm_company'
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    full_name VARCHAR(255),
    user_type VARCHAR(50) NOT NULL, -- 'property_manager', 'contractor', 'owner'
    organization_id UUID REFERENCES organizations(id),
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Properties
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    address JSONB NOT NULL, -- {street, city, state, zip, unit}
    property_type VARCHAR(50), -- 'single_family', 'condo', 'townhouse', 'multi_family'
    units INTEGER DEFAULT 1,
    year_built INTEGER,
    square_feet INTEGER,
    property_data JSONB, -- Flexible storage for property-specific data
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Property Memory (AI Agent Storage)
CREATE TABLE property_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) NOT NULL,
    category VARCHAR(100), -- 'access', 'equipment', 'preferences', 'history'
    key VARCHAR(255),
    value JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(property_id, category, key)
);

-- Projects (Maintenance Requests)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) NOT NULL,
    organization_id UUID REFERENCES organizations(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100), -- 'plumbing', 'electrical', 'roofing', etc.
    urgency VARCHAR(50), -- 'emergency', 'urgent', 'routine', 'preventive'
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sourcing', 'bidding', 'awarded', 'in_progress', 'completed'
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    timeline_start DATE,
    timeline_end DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Project Files
CREATE TABLE project_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    file_url TEXT NOT NULL, -- S3 URL
    file_type VARCHAR(50), -- 'photo', 'video', 'document', 'quote'
    file_name VARCHAR(255),
    file_size INTEGER,
    metadata JSONB, -- Store extracted text, AI analysis, etc.
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Contractors
CREATE TABLE contractors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    company_name VARCHAR(255),
    license_number VARCHAR(100),
    license_verified BOOLEAN DEFAULT FALSE,
    insurance_verified BOOLEAN DEFAULT FALSE,
    insurance_expiry DATE,
    trades TEXT[], -- Array of trade categories
    service_areas JSONB, -- Geographic coverage
    rating DECIMAL(3,2), -- Average rating
    jobs_completed INTEGER DEFAULT 0,
    response_rate DECIMAL(3,2), -- Percentage
    average_response_time INTEGER, -- In hours
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invitations
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    contractor_id UUID REFERENCES contractors(id) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'viewed', 'accepted', 'declined'
    invited_at TIMESTAMPTZ DEFAULT NOW(),
    viewed_at TIMESTAMPTZ,
    responded_at TIMESTAMPTZ,
    response_note TEXT,
    UNIQUE(project_id, contractor_id)
);

-- Quotes/Bids
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    contractor_id UUID REFERENCES contractors(id) NOT NULL,
    invitation_id UUID REFERENCES invitations(id),
    raw_quote JSONB, -- Original format storage
    standardized_quote JSONB, -- AI-standardized format
    total_price DECIMAL(10,2),
    timeline_days INTEGER,
    includes TEXT[],
    excludes TEXT[],
    payment_terms TEXT,
    valid_until DATE,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'submitted', 'awarded', 'declined'
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Awards
CREATE TABLE awards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    quote_id UUID REFERENCES quotes(id) NOT NULL,
    contractor_id UUID REFERENCES contractors(id) NOT NULL,
    awarded_by UUID REFERENCES users(id),
    awarded_at TIMESTAMPTZ DEFAULT NOW(),
    contract_signed BOOLEAN DEFAULT FALSE,
    work_started_at TIMESTAMPTZ,
    work_completed_at TIMESTAMPTZ,
    final_price DECIMAL(10,2),
    UNIQUE(project_id)
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) NOT NULL,
    sender_id UUID REFERENCES users(id) NOT NULL,
    recipient_type VARCHAR(50), -- 'all', 'contractor', 'pm', 'owner'
    recipient_id UUID REFERENCES users(id),
    message_text TEXT,
    attachments JSONB,
    read_by UUID[], -- Array of user IDs who have read
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Agent Logs
CREATE TABLE ai_agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_type VARCHAR(50), -- 'smartscope', 'sourcing', 'memory'
    project_id UUID REFERENCES projects(id),
    property_id UUID REFERENCES properties(id),
    input_data JSONB,
    output_data JSONB,
    tokens_used INTEGER,
    processing_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔐 Row Level Security Policies

```sql
-- Users can only see their own organization's data
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
CREATE POLICY org_properties ON properties
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

-- Contractors can see projects they're invited to
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY contractor_projects ON projects
    FOR SELECT USING (
        id IN (SELECT project_id FROM invitations WHERE contractor_id IN (
            SELECT id FROM contractors WHERE user_id = auth.uid()
        ))
    );
```

## 📊 Indexes for Performance

```sql
CREATE INDEX idx_properties_org ON properties(organization_id);
CREATE INDEX idx_projects_property ON projects(property_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_quotes_project ON quotes(project_id);
CREATE INDEX idx_contractors_trades ON contractors USING GIN(trades);
CREATE INDEX idx_messages_project ON messages(project_id);
CREATE INDEX idx_property_memory_lookup ON property_memory(property_id, category);
```

## 🔄 Real-time Subscriptions

```sql
-- Enable realtime for key tables
ALTER PUBLICATION supabase_realtime ADD TABLE projects;
ALTER PUBLICATION supabase_realtime ADD TABLE quotes;
ALTER PUBLICATION supabase_realtime ADD TABLE messages;
ALTER PUBLICATION supabase_realtime ADD TABLE invitations;
```

## 📱 Mobile Offline Support

Key tables to sync for offline:
- properties (read-only)
- projects (read/write)
- project_files (write for upload queue)
- messages (read/write with sync)

## 🎯 Next Steps for Database

1. Create migrations for each table
2. Set up RLS policies
3. Create database functions for complex queries
4. Set up triggers for updated_at
5. Configure real-time subscriptions
6. Set up backup strategy