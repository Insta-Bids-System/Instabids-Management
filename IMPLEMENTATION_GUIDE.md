# InstaBids-Management Implementation Guide

## 🎯 How to Use This Documentation

### Documentation Structure
```
docs/
├── VISION.md              # Business strategy & goals
├── PAIN_POINTS.md         # Problems we solve
├── FEATURE_BREAKDOWN.md   # All features to build
├── DATABASE_SCHEMA.md     # Supabase structure
├── TECH_STACK.md         # Technology decisions
└── ROADMAP.md            # Week-by-week plan
```

## 🏗️ Building Approach

### Step 1: Feature Specification
For each feature in `FEATURE_BREAKDOWN.md`, create a spec:

```bash
# Example for first feature
/specify user authentication with property manager and contractor roles, email/phone verification, portfolio management
```

This creates: `specs/user-authentication/spec.md`

### Step 2: Technical Planning
After spec is complete:

```bash
/plan user-authentication
```

This creates: `specs/user-authentication/plan.md`

### Step 3: Task Generation
After plan is approved:

```bash
/tasks user-authentication
```

This creates: `specs/user-authentication/tasks.md` with 25-30 tasks

### Step 4: Implementation
Execute tasks in order, marking parallel tasks [P]

## 📋 Feature Build Order (MVP)

### Sprint 1: Foundation (Must Have)
1. **User Authentication** → `/specify user authentication...`
2. **Property Management** → `/specify property portfolio...`
3. **Project Creation** → `/specify maintenance project...`

### Sprint 2: Core Value (Critical)
4. **SmartScope Engine** → `/specify AI scope standardization...`
5. **Contractor Matching** → `/specify contractor discovery...`
6. **Quote Collection** → `/specify quote collection...`

### Sprint 3: Marketplace (Essential)
7. **Bid Comparison** → `/specify bid comparison...`
8. **Communication Hub** → `/specify messaging system...`
9. **Award Workflow** → `/specify bid award...`

## 🗄️ Database Setup

### 1. Create Supabase Project
```bash
# Install Supabase CLI
npm install -g supabase

# Initialize project
supabase init

# Link to project
supabase link --project-ref [your-project-id]
```

### 2. Run Migrations
Use schema from `docs/DATABASE_SCHEMA.md`:

```bash
# Create migration
supabase migration new initial_schema

# Copy schema to migration file
# Then push to database
supabase db push
```

### 3. Set Up RLS
Enable Row Level Security for all tables

### 4. Configure Real-time
Enable real-time for projects, quotes, messages

## 🚀 Quick Start Commands

### Local Development
```bash
# Clone and setup
git clone [repo]
cd InstaBids-Management
npm install

# Start Supabase locally
supabase start

# Run web app
cd web
npm run dev

# Run mobile app
cd mobile
expo start

# Run API
cd api
uvicorn main:app --reload
```

### Environment Variables
```env
# .env.local (web)
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
OPENAI_API_KEY=

# .env (api)
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
OPENAI_API_KEY=
AWS_S3_BUCKET=
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
```

## 📊 Success Metrics Tracking

### Week 1 Goals
- [ ] Auth system working
- [ ] 5 test users created
- [ ] Properties CRUD complete

### Week 4 Goals
- [ ] SmartScope 80% accurate
- [ ] 10 test projects created
- [ ] Photo upload working

### Week 8 Goals
- [ ] 50 contractors registered
- [ ] Quote comparison working
- [ ] 4+ bids per project

### Week 12 Goals
- [ ] 10 beta PMs active
- [ ] 25 projects completed
- [ ] <4hr bid response time

## 🔄 Development Workflow

### For Each Feature:
1. **Read** pain point from `PAIN_POINTS.md`
2. **Find** feature in `FEATURE_BREAKDOWN.md`
3. **Run** `/specify [feature]` command
4. **Review** and resolve clarifications
5. **Run** `/plan [feature]` command
6. **Run** `/tasks [feature]` command
7. **Execute** tasks using TDD approach
8. **Test** with real data
9. **Deploy** to staging
10. **Validate** with beta users

## 🎯 Next Immediate Actions

### Today:
1. Set up Supabase project
2. Create initial database schema
3. Run `/specify user authentication`

### This Week:
1. Complete authentication system
2. Build property management
3. Start project creation flow

### This Month:
1. Launch MVP with core features
2. Recruit 10 beta property managers
3. Process 25 real projects

## 📚 Key Documents Reference

When building, always reference:
- **Pain Points**: Why we're building this
- **Vision**: Where we're going
- **Constitution**: How we build (principles)
- **Tech Stack**: What we use
- **Database Schema**: How data is structured

## 🚦 Go/No-Go Decisions

### Before Building:
- Pain point validated? ✓
- Feature specified? ✓
- Plan approved? ✓
- Tasks clear? ✓

### Before Launching:
- Core features working? ✓
- Beta users recruited? ✓
- Monitoring in place? ✓
- Support ready? ✓

## 💡 Remember

1. **Start Simple**: MVP first, then iterate
2. **User Focus**: Solve real PM problems
3. **Test Early**: Get feedback quickly
4. **Document**: Keep specs updated
5. **Measure**: Track all metrics

---

**Ready to Build?** Start with:
```
/specify user authentication with property manager and contractor roles
```