# Technical Plan: User Authentication System

## Architecture Overview

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL + Auth)
- **Frontend**: Next.js 14 (Web) + React Native (Mobile)
- **Authentication**: Supabase Auth with JWT
- **Email Service**: Supabase Email (built-in)
- **SMS Service**: Twilio (future)

### Component Architecture
```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js Web   │────▶│  FastAPI     │────▶│  Supabase   │
└─────────────────┘     │  Backend     │     │  Database   │
                        │  (Port 8000) │     │  + Auth     │
┌─────────────────┐     │              │     └─────────────┘
│  React Native   │────▶│              │
└─────────────────┘     └──────────────┘
```

## Implementation Approach

### Phase 1: Backend Foundation (Hours 1-4)
1. Set up FastAPI project structure
2. Configure Supabase client
3. Create auth endpoints
4. Add validation and error handling

### Phase 2: Database Layer (Hours 5-6)
1. Extend user_profiles table
2. Add auth audit logs
3. Create stored procedures
4. Set up RLS policies### Phase 3: Frontend Components (Hours 7-10)
1. Create auth context/hooks
2. Build registration form
3. Build login form
4. Add protected routes

### Phase 4: Integration & Testing (Hours 11-12)
1. End-to-end testing
2. Error handling
3. Performance optimization
4. Security audit

## API Endpoints Design

### Registration
```python
POST /api/auth/register
Body: {
    "email": "user@example.com",
    "password": "SecurePass123!",
    "user_type": "property_manager",
    "full_name": "John Doe",
    "organization_name": "Doe Properties"
}
Response: {
    "user_id": "uuid",
    "email": "user@example.com",
    "requires_verification": true
}
```### Login
```python
POST /api/auth/login
Body: {
    "email": "user@example.com",
    "password": "SecurePass123!"
}
Response: {
    "access_token": "jwt...",
    "refresh_token": "jwt...",
    "user": {...}
}
```

### Verify Email
```python
POST /api/auth/verify-email
Body: {
    "token": "verification_token"
}
Response: {
    "verified": true
}
```

## Database Schema Extensions

### Auth Audit Log Table
```sql
CREATE TABLE auth_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    event_type VARCHAR(50) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```## Security Measures

### Password Policy
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 number
- No common passwords (check against list)
- Bcrypt with cost factor 12

### Rate Limiting
- Registration: 5 attempts per hour per IP
- Login: 10 attempts per hour per email
- Password reset: 3 attempts per hour per email

### Session Management
- JWT expires in 1 hour
- Refresh token expires in 30 days
- Device fingerprinting for security
- Automatic logout on suspicious activity

## Frontend Components Structure

```typescript
/components/auth/
├── LoginForm.tsx
├── RegisterForm.tsx
├── ForgotPasswordForm.tsx
├── VerifyEmailForm.tsx
├── AuthProvider.tsx
└── ProtectedRoute.tsx

/hooks/
├── useAuth.ts
├── useSession.ts
└── useSupabase.ts
```

## Testing Strategy

### Unit Tests
- Password validation logic
- JWT token generation
- Input sanitization### Integration Tests
- Complete registration flow
- Login with valid/invalid credentials
- Password reset flow
- Session refresh

### Security Tests
- SQL injection attempts
- XSS prevention
- CSRF protection
- Rate limiting effectiveness

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Supabase Auth downtime | Implement retry logic with exponential backoff |
| Email delivery failures | Add webhook for delivery status, SMS fallback |
| Brute force attacks | Rate limiting + CAPTCHA after 3 failed attempts |
| Session hijacking | Device fingerprinting + IP validation |

## Dependencies

```python
# requirements.txt
fastapi==0.109.0
supabase==2.3.0
pydantic==2.5.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
email-validator==2.1.0
```

---
Status: READY FOR REVIEW
Estimated Time: 12 hours
Next Step: Generate tasks with /tasks