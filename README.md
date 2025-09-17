# InstaBids Management Platform

A comprehensive property management system for coordinating maintenance and repairs across multiple properties with AI-powered features.

## 🎯 Overview

InstaBids Management transforms how property managers handle maintenance by providing:
- **SmartScope™**: AI-powered project scoping from photos
- **Unified contractor management**: Streamlined bidding and communication
- **Intelligent project routing**: Match projects with the right contractors
- **Mobile-first design**: Full functionality on iOS and Android

## 🏗️ Tech Stack

- **Frontend**: Next.js 14 (Web) + React Native (Mobile)
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-4 Vision
- **Storage**: AWS S3

## 📁 Project Structure

```
InstaBids-Management/
├── docs/                 # Documentation
├── web/                  # Next.js web app
├── mobile/              # React Native app
├── api/                 # FastAPI backend
├── migrations/          # Database migrations
└── specs/              # Feature specifications
```

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

## 📊 Features

### Phase 1 (Weeks 1-4)
- ✅ User Authentication
- ⏳ Property Management
- ⏳ Project Creation
- ⏳ SmartScope MVP

### Phase 2 (Weeks 5-8)
- Quote Collection
- Basic Standardization
- Notification System
- Analytics Dashboard

### Phase 3 (Weeks 9-12)
- AI Recommendations
- Mobile Apps
- Contractor Portal
- Advanced Features

## 🔗 Links

- [Documentation](./docs/)
- [Supabase Dashboard](https://supabase.com/dashboard/project/lmbpvkfcfhdfaihigfdu)

## 📝 License

Proprietary - All rights reserved