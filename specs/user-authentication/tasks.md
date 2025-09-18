# Task List: User Authentication System

## Setup Tasks (30 min)
- [x] Create `api/` directory structure
- [ ] Create `web/` directory structure  
- [x] Initialize FastAPI project
- [ ] Initialize Next.js project
- [x] Create `.env.example` file with all required vars

## Backend API Tasks (4 hours)

### Project Setup [P]
- [x] Create `api/requirements.txt` with dependencies
- [x] Create `api/main.py` with FastAPI app
- [x] Create `api/config.py` for environment variables
- [x] Set up Supabase client in `api/services/supabase.py`
- [x] Create `api/models/` directory for Pydantic models

### Authentication Endpoints [P]
- [x] Create `api/models/auth.py` with request/response models
- [x] Create `api/routers/auth.py` router file
- [x] Implement `POST /api/auth/register` endpoint
- [x] Implement `POST /api/auth/login` endpoint  
- [x] Implement `POST /api/auth/logout` endpoint
- [x] Implement `POST /api/auth/refresh` endpoint
- [x] Implement `POST /api/auth/verify-email` endpoint
- [x] Implement `POST /api/auth/reset-password` endpoint### Middleware & Security
- [x] Create `api/middleware/rate_limit.py` 
- [x] Create `api/middleware/auth.py` for JWT validation
- [x] Add CORS configuration to main.py
- [x] Implement input validation for all endpoints
- [x] Add error handling middleware

## Database Tasks (1 hour)

### Migration 002 [P]
- [x] Create `migrations/002_auth_extensions.sql`
- [x] Add auth_audit_log table
- [x] Add password_history table
- [x] Add user_sessions table
- [x] Apply migration to Supabase
- [x] Update `migrations/applied.md`

## Frontend Tasks (4 hours)

### Next.js Setup [P]
- [x] Create `web/package.json` with dependencies
- [x] Configure `web/next.config.js`
- [x] Set up `web/tailwind.config.js`
- [x] Create `web/.env.local.example`
- [x] Install Supabase client libraries### Auth Components
- [x] Create `web/lib/supabase.ts` client
- [x] Create `web/contexts/AuthContext.tsx`
- [x] Create `web/hooks/useAuth.ts`
- [x] Create `web/components/auth/LoginForm.tsx`
- [x] Create `web/components/auth/RegisterForm.tsx`
- [x] Create `web/components/auth/ForgotPasswordForm.tsx`
- [x] Create `web/components/auth/VerifyEmailForm.tsx`

### Pages & Routes
- [x] Create `web/app/login/page.tsx`
- [x] Create `web/app/register/page.tsx`
- [x] Create `web/app/forgot-password/page.tsx`
- [x] Create `web/app/verify-email/page.tsx`
- [x] Create `web/app/dashboard/page.tsx` (protected)
- [x] Implement route protection middleware

## Testing Tasks (2 hours)

### API Tests [P]
- [ ] Write tests for registration endpoint
- [ ] Write tests for login endpoint
- [ ] Write tests for password reset
- [ ] Write tests for rate limiting
- [ ] Test invalid input handling### Integration Tests
- [ ] Test complete registration flow
- [ ] Test email verification flow
- [ ] Test password reset flow
- [ ] Test session refresh
- [ ] Test logout and session cleanup

## Documentation Tasks (30 min)

- [x] Create `api/README.md` with setup instructions
- [ ] Create `web/README.md` with setup instructions
- [ ] Document API endpoints in `docs/API.md`
- [ ] Update main README.md with auth info
- [ ] Create auth flow diagrams

## Deployment Prep (30 min)

- [ ] Create `docker-compose.yml` for local dev
- [ ] Create `api/Dockerfile`
- [ ] Create `web/Dockerfile`
- [ ] Set up GitHub Actions workflow
- [ ] Configure environment variables

---
**Total Tasks**: 70
**Estimated Time**: 12 hours
**[P]** = Can be done in parallel

## Execution Order
1. Setup tasks first
2. Backend API + Database in parallel
3. Frontend after API is working
4. Testing throughout
5. Documentation last