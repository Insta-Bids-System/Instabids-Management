# InstaBids Management Platform

A marketplace platform connecting property managers with qualified contractors for maintenance and repairs, featuring AI-powered project scoping and quote standardization.

## 🎯 Overview

InstaBids Management revolutionizes property maintenance by creating a frictionless marketplace that:
- **Eliminates site visits**: SmartScope™ AI analyzes photos to create detailed work scopes
- **Standardizes quotes**: Multi-format quote collection with automatic standardization
- **Auto-matches contractors**: Intelligent matching based on trade, location, and availability
- **Saves 50% time**: <2 minute project creation with automated contractor invitations
- **Ensures quality**: Verified contractor credentials and performance tracking

## 🏗️ Tech Stack

- **Web App**: Next.js 14 + TypeScript + Tailwind CSS
- **Mobile App**: React Native + Expo SDK 53 + TypeScript
- **Backend**: FastAPI (Python) + Pydantic v2
- **Database**: Supabase (PostgreSQL) + Row Level Security
- **AI**: OpenAI GPT-4 Vision for SmartScope™
- **Shared Logic**: Zod schemas + TypeScript interfaces
- **Storage**: AWS S3 + CloudFront CDN

## 📁 Project Structure

```
InstaBids-Management/
├── docs/                 # Documentation
├── web/                  # Next.js web application
│   └── src/components/  # Web-specific UI components
├── mobile/              # React Native Expo app
│   └── src/            # Mobile-specific UI components
├── packages/shared/     # Shared logic between platforms
│   ├── types/          # TypeScript interfaces
│   ├── schemas/        # Zod validation schemas
│   └── api/            # API client functions
├── api/                # FastAPI backend
├── migrations/         # Database migrations
├── specs/             # Feature specifications
└── UI_DEVELOPMENT_GUIDE.md # UI consistency rules
```

## 🎨 UI Development Approach

We build UI components for **BOTH web and mobile in parallel**:
- Shared business logic in `packages/shared/`
- Separate UI implementations for optimal platform experience
- Consistent functionality across all platforms
- See [UI_DEVELOPMENT_GUIDE.md](UI_DEVELOPMENT_GUIDE.md) for patterns

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase CLI
- Expo CLI (for mobile)

### Installation

1. Clone the repository
```bash
git clone https://github.com/Insta-Bids-System/Instabids-Management.git
cd Instabids-Management
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

3. Install dependencies
```bash
# Web
cd web && npm install

# Mobile
cd ../mobile && npm install

# API
cd ../api && pip install -r requirements.txt
```

4. Run migrations
```bash
supabase db push
```

5. Start development servers
```bash
# Web
cd web && npm run dev

# Mobile
cd mobile && expo start

# API
cd api && uvicorn main:app --reload
```

## 📊 Development Status

### ✅ Week 1-2: Foundation (COMPLETE)
- ✅ Authentication System (9 endpoints, JWT, rate limiting)
- ✅ Property Management (14 endpoints, full CRUD)
- ✅ Database Schema (9 tables, RLS policies)
- ✅ File Upload System

### 🚧 Week 2-3: Marketplace Core (IN PROGRESS)
- ✅ Project Creation Spec & Plan
- ✅ Contractor Onboarding Spec & Plan  
- ✅ Quote Submission Spec & Plan
- ✅ SmartScope AI Spec & Plan
- ⏳ SmartScope Supabase alignment (schema realignment, cost table, RLS policies still pending)
- ⏳ Project API Implementation
- ⏳ Contractor Registration System
- ⏳ Quote Collection Engine

### 📋 Week 3-4: Intelligence Layer (PLANNED)
- SmartScope AI Integration (OpenAI Vision)
- Quote Standardization Engine
- Contractor Matching Algorithm
- Automated Invitations

### 🎯 Week 4: Beta Ready
- Mobile App Components
- End-to-End Testing
- Production Deployment
- 10 PM + 50 Contractor Onboarding

## 🔗 Links

- [Documentation](./docs/)
- [Supabase Dashboard](https://supabase.com/dashboard/project/lmbpvkfcfhdfaihigfdu)

## 📝 License

Proprietary - All rights reserved