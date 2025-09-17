# InstaBids-Management Project Context

## 🎯 Project Overview
**What**: Property management platform for maintenance coordination
**Status**: Pre-MVP Development
**Target**: 10 PMs, 50 contractors, 25 projects by Week 12

## 🗄️ Supabase Configuration
```yaml
Project URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Project ID: lmbpvkfcfhdfaihigfdu
Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...Tnmg
Service Key: [NEVER COMMIT]
```

## 📁 Project Structure
```
InstaBids-Management/
├── CLAUDE.md              # THIS FILE - Always read first
├── PROGRESS.md           # Current sprint status
├── docs/                 # Master documentation
│   ├── VISION.md        # Business strategy
│   ├── PAIN_POINTS.md   # Problems we solve
│   ├── FEATURE_BREAKDOWN.md # All features
│   ├── DATABASE_SCHEMA.md   # Supabase schema
│   ├── TECH_STACK.md    # Technology decisions
│   └── ROADMAP.md       # 12-week plan
├── specs/               # Feature specifications
├── migrations/          # Database migrations
│   └── applied.md      # Track what's in Supabase
├── src/                # Source code
└── tests/             # Test suites
```

## 🏗️ Current Sprint (Week 1)
**Focus**: Authentication & Property Management
**Features**:
1. User Authentication [IN PROGRESS]
2. Property Portfolio [NOT STARTED]
3. Project Creation [NOT STARTED]

## ✅ Completed Features
<!-- As we complete features, move them here -->
- None yet

## 🔄 In Progress
- [ ] User Authentication System
  - [ ] Spec created: `specs/user-authentication/spec.md`
  - [ ] Plan created: `specs/user-authentication/plan.md`
  - [ ] Tasks generated: `specs/user-authentication/tasks.md`
  - [ ] Database tables created
  - [ ] API endpoints built
  - [ ] Frontend connected

## 📊 Database Status
**Schema Version**: 0.0.0
**Last Migration**: None
**Tables Created**: None

See `migrations/applied.md` for what's in production

## 🔧 Development Environment
```bash
# Local Supabase
supabase start

# Web App (Next.js)
cd web && npm run dev # http://localhost:3000

# Mobile App (React Native)
cd mobile && expo start

# API (FastAPI)
cd api && uvicorn main:app --reload # http://localhost:8000
```

## 🎯 Key Decisions Made
1. **Tech Stack**: Next.js + React Native + FastAPI + Supabase
2. **AI Provider**: OpenAI GPT-4 Vision for SmartScope
3. **File Storage**: AWS S3
4. **Auth**: Supabase Auth (not Auth0)
5. **Mobile First**: React Native from day 1

## 🚀 Next Actions
1. Complete user authentication spec
2. Create Supabase project
3. Run initial migrations
4. Build auth API endpoints
5. Create registration UI

## 📝 How to Resume Work

When starting a new chat session:
1. I'll read this CLAUDE.md first
2. Check PROGRESS.md for current sprint
3. Look at migrations/applied.md for DB state
4. Continue from "Next Actions"

## 🔗 Important Links
- Supabase Dashboard: https://supabase.com/dashboard/project/lmbpvkfcfhdfaihigfdu
- GitHub Repo: https://github.com/Insta-Bids-System/Instabids-Management
- Staging Environment: [TO BE ADDED]
- Production: [TO BE ADDED]

## ⚠️ Critical Notes
- NEVER commit service keys
- Always update migrations/applied.md after DB changes
- Update PROGRESS.md after completing tasks
- Keep this file under 200 lines

---
Last Updated: 2025-01-17
Current Week: 1 of 12