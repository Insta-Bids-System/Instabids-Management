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
├── UI_DEVELOPMENT_GUIDE.md # UI consistency rules
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
├── web/                 # Next.js web application
│   └── src/components/  # Web-specific UI components
├── mobile/              # React Native Expo app
│   └── src/             # Mobile-specific UI components
├── packages/shared/     # Shared logic between platforms
│   ├── types/          # TypeScript interfaces
│   ├── schemas/        # Zod validation schemas
│   └── api/            # API client functions
├── api/                # FastAPI backend
└── tests/             # Test suites
```

## 🏗️ Current Sprint (Week 1)
**Focus**: Authentication & Property Management
**Features**:
1. User Authentication [95% COMPLETE] ✅ PRODUCTION READY
2. Property Management [40% COMPLETE]
3. Project Creation [NOT STARTED]

## ✅ Completed Features
- [x] **User Authentication System** - PRODUCTION READY
  - [x] Spec created: `specs/user-authentication/spec.md`
  - [x] Plan created: `specs/user-authentication/plan.md`
  - [x] Tasks generated: `specs/user-authentication/tasks.md`
  - [x] Database tables created (6 tables)
  - [x] API endpoints built (9 endpoints)
  - [x] Frontend components created
  - [x] Testing & documentation completed
  - [x] All critical errors fixed (20+ issues resolved)
  - [x] Production deployment ready

## 🔄 In Progress
  
- [x] Property Management System
  - [x] Spec created: `specs/property-management/spec.md`
  - [x] Plan created: `specs/property-management/plan.md`
  - [x] Tasks generated: `specs/property-management/tasks.md` (136 tasks)
  - [x] Database migration created
  - [x] API endpoints built (14 endpoints)
  - [ ] Frontend components
  - [ ] Testing & documentation

## 📊 Database Status
**Schema Version**: 0.0.3
**Last Migration Applied**: 002_auth_extensions (2025-01-17)
**Next Migration**: 003_property_management (READY)
**Tables Created**: 9 tables (organizations, user_profiles, properties, auth tables)
**Pending Tables**: property_groups, property_group_members, property_audit_log

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
1. Apply 003_property_management migration to Supabase
2. Build property management frontend components
3. Create property list and detail pages
4. Implement property import/export UI
5. Test property API endpoints
6. Begin project creation feature

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

## 🎨 UI Development Approach (CRITICAL)
**We build UI for BOTH web and mobile in PARALLEL**
- Every UI component gets built twice: once for web (Next.js/Tailwind), once for mobile (React Native)
- Business logic is SHARED via packages/shared/
- UI is SEPARATE but consistent in functionality
- This adds only 10-15% overhead vs 40% for fully shared UI
- See UI_DEVELOPMENT_GUIDE.md for detailed patterns

## ⚠️ Critical Notes
- NEVER commit service keys
- Always update migrations/applied.md after DB changes
- Update PROGRESS.md after completing tasks
- Build UI for BOTH platforms when adding features
- Keep this file under 200 lines

---
Last Updated: 2025-01-18
Current Week: 2 of 12