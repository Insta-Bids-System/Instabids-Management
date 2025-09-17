# InstaBids Master Alignment Document

## 🎯 Vision → User Stories → Build Alignment

This document ensures complete alignment between our vision, user stories, and what we're building.

## 📊 Alignment Score: 100% (After Pivot)

### Core Value Proposition Alignment

| Vision Element | User Story Coverage | What We're Building | Status |
|---|---|---|---|
| **AI-Powered Contractor Sourcing** | Story 3.1: Auto-invite qualified contractors | Contractor matching algorithm in project-creation spec | ✅ Aligned |
| **Standardized Bidding** | Story 3.2: See all bids in same format | Quote standardization engine in quote-submission spec | ✅ Aligned |
| **50% Time Savings** | Story 2.1: Create project in <2 minutes | Project creation wizard in spec | ✅ Aligned |
| **No Site Visits** | Story 2.3: Virtual property access | SmartScope AI + virtual walkthrough | ✅ Aligned |
| **Competitive Quotes** | Story 6.1: Get multiple bids fast | Multi-channel invitation system | ✅ Aligned |

## 🗺️ Complete Feature Mapping

### Phase 1: Foundation (Weeks 1-2) ✅ COMPLETE
**What We Built:**
- ✅ Authentication System (9 endpoints)
- ✅ Property Management (14 endpoints)
- ✅ File Upload System
- ✅ Database Schema

### Phase 2: Marketplace Core (Week 2-3) 🚧 IN PROGRESS

#### 1. Project Creation System
**User Stories Covered:**
- ✅ Story 2.1: Create project in <2 minutes
- ✅ Story 2.2: Upload documentation
- ✅ Story 2.3: Virtual walk-through

**Specification:** `specs/project-creation/spec.md`
**Key Features:**
- Property selection from existing list
- Issue description with category
- Urgency levels (Emergency/Urgent/Routine)
- Photo/video upload (10 photos, 3 videos)
- Budget ranges
- Auto contractor matching
- Virtual access instructions

#### 2. Contractor Onboarding
**User Stories Covered:**
- ✅ Story 5.1: Contractor registration
- ✅ Story 5.2: Profile setup

**Specification:** `specs/contractor-onboarding/spec.md`
**Key Features:**
- Business registration with verification
- License/insurance upload
- Service area definition (ZIP codes)
- Trade specialties selection
- Emergency availability settings
- Portfolio showcase

#### 3. Quote Submission System
**User Stories Covered:**
- ✅ Story 6.3: Submit bid (multiple formats)
- ✅ Story 6.4: Track bid status
- ✅ Story 3.2: Review bids in standard format

**Specification:** `specs/quote-submission/spec.md`
**Key Features:**
- 4 submission methods (PDF/Email/Photo/Form)
- Automatic standardization
- Side-by-side comparison
- Confidence scoring
- Version control

### Phase 3: Intelligence Layer (Week 3-4)

#### 4. SmartScope AI
**User Stories Covered:**
- ✅ Story 2.2: Contractors understand without site visits
- ✅ Story 6.2: Review project details clearly

**Specification:** `specs/smartscope-ai/spec.md`
**Key Features:**
- OpenAI Vision integration
- Automatic issue identification
- Severity assessment
- Materials list generation
- Time estimates
- 92% confidence targeting

#### 5. Invitation & Matching
**User Stories Covered:**
- ✅ Story 3.1: Invite qualified contractors
- ✅ Story 6.1: Receive job invitations

**Built Into:** Project Creation + Contractor specs
**Key Features:**
- Trade category matching
- Service area filtering
- Availability checking
- Staggered invitations
- SMS/Email notifications

## 📋 Database Schema Alignment

### Existing Tables (Keep & Use)
```sql
-- Already Built
organizations (✅ for PM companies)
user_profiles (✅ extend for contractors)
properties (✅ for project linkage)

-- Add These Tables
projects (Link properties to work)
contractor_profiles (Extended user data)
quotes (Bid submissions)
quote_items (Standardized line items)
invitations (Contractor invites)
project_media (Photos/videos)
```

### New Migration Needed
```sql
-- 004_marketplace_core.sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  property_id UUID REFERENCES properties(id),
  title VARCHAR(255),
  description TEXT,
  category VARCHAR(50),
  urgency urgency_level,
  bid_deadline TIMESTAMP,
  budget_min DECIMAL,
  budget_max DECIMAL,
  status project_status,
  smartscope_analysis JSONB,
  virtual_access JSONB
);

CREATE TABLE quotes (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  contractor_id UUID REFERENCES user_profiles(id),
  submission_method VARCHAR(50),
  original_format VARCHAR(50),
  standardized_data JSONB,
  confidence_score DECIMAL,
  status quote_status
);
```

## 🎯 Sprint Execution Plan

### Week 2 Remaining (Must Complete)
**Monday-Tuesday: Project Creation**
- [ ] Create projects table migration
- [ ] Build project API endpoints
- [ ] Create project frontend components
- [ ] Integrate with properties

**Wednesday-Thursday: Contractor System**
- [ ] Extend user_profiles for contractors
- [ ] Build contractor API endpoints
- [ ] Create onboarding flow
- [ ] Service area management

**Friday: Quote Submission**
- [ ] Create quotes table
- [ ] Build submission endpoints
- [ ] Create upload interfaces

### Week 3 (Intelligence & Standardization)
**Monday-Tuesday: SmartScope AI**
- [ ] OpenAI Vision integration
- [ ] Scope extraction logic
- [ ] Confidence scoring

**Wednesday-Thursday: Standardization**
- [ ] OCR integration
- [ ] Pattern matching
- [ ] Comparison interface

**Friday: Testing & Polish**
- [ ] End-to-end testing
- [ ] UI polish
- [ ] Performance optimization

### Week 4 (Beta Ready)
**Monday: Award & Communication**
- [ ] Award workflow
- [ ] Messaging system
- [ ] Notifications

**Tuesday-Wednesday: Mobile**
- [ ] Mobile photo capture
- [ ] Contractor mobile app
- [ ] Push notifications

**Thursday-Friday: Beta Launch**
- [ ] Deploy to production
- [ ] Onboard 10 PMs
- [ ] Monitor and fix

## 📊 Success Metrics Tracking

### Must Hit by Week 4
| Metric | Target | How We'll Achieve |
|---|---|---|
| Project creation time | <2 minutes | Wizard UI, property pre-fill |
| Bids per project | 3+ | Auto-invite, staggered sends |
| Time to first bid | <4 hours | SMS alerts, easy submission |
| Quote standardization | 80% accurate | OCR + AI + patterns |
| Contractor response rate | 70% | Multi-channel, simple submit |

## 🔄 What We're NOT Building (MVP)
- ❌ Complex property analytics
- ❌ Property groups/portfolios
- ❌ Payment processing
- ❌ Background checks
- ❌ Complex messaging threads
- ❌ Change orders
- ❌ Progress tracking
- ❌ Invoicing

## ✅ Validation Checklist

### Every User Story Mapped
- [x] Epic 1: Account Management → Auth + Properties
- [x] Epic 2: Project Creation → Project spec
- [x] Epic 3: Contractor Selection → Matching + Invites
- [x] Epic 5: Contractor Onboarding → Contractor spec
- [x] Epic 6: Bidding Process → Quote submission spec

### Core Problems Solved
- [x] PMs spending 15+ hours/month → <2min projects
- [x] 30-50% PM markup → Direct competitive bids
- [x] Site visit requirements → Virtual + AI scope
- [x] Non-standard quotes → Standardized comparison
- [x] Finding contractors → Auto-matching

### Technical Feasibility
- [x] Reuse property foundation
- [x] Extend auth for contractors
- [x] Add marketplace tables
- [x] Integrate AI services
- [x] Support multiple formats

## 🚀 Next Immediate Actions

1. **Create migration 004_marketplace_core.sql**
2. **Run /plan for project-creation**
3. **Run /tasks for project-creation**
4. **Start building projects table**
5. **Create project API endpoints**

## 📝 Commands to Run Next

```bash
# Generate technical plans
/plan project-creation
/plan contractor-onboarding  
/plan quote-submission

# Generate task lists
/tasks project-creation
/tasks contractor-onboarding
/tasks quote-submission

# After Week 3
/plan smartscope-ai
/tasks smartscope-ai
```

---

## ✅ Alignment Confirmation

**We are now 100% aligned:**
- Every user story has a specification
- Every specification maps to features
- Every feature has clear implementation path
- Database schema supports all needs
- Timeline is realistic and focused
- Success metrics match user stories

**The pivot is complete. We're building the RIGHT thing.**