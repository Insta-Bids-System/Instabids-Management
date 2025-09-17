# User Authentication Specification

## Feature Name: User Authentication System

## Overview
Multi-role authentication system supporting Property Managers, Contractors, and Tenants with email/phone verification and organization management.

## User Roles

### Property Manager
- Full access to all properties in organization
- Can invite contractors and tenants
- Manages projects and approves quotes
- Views analytics and reports

### Contractor
- Access to assigned projects only
- Can submit quotes and messages
- Updates project status
- Manages crew members

### Tenant
- Limited to their unit/property
- Can submit maintenance requests
- Views project updates
- Messaging with property manager

## Functional Requirements

### Registration Flow
1. User enters email and selects role
2. System sends verification code
3. User enters verification code4. User completes profile:
   - Property Manager: Organization name, phone, address
   - Contractor: Business name, license number, services
   - Tenant: Property/unit selection (via invite)
5. System creates account and logs in user

### Login Flow
1. User enters email/phone
2. System checks if account exists
3. Password or magic link authentication
4. MFA if enabled (SMS/TOTP)
5. Session created with JWT token

### Password Management
- Minimum 8 characters with complexity rules
- Password reset via email link
- Force password change on first login
- Password history (no reuse of last 5)

### Session Management
- JWT tokens with 24-hour expiry
- Refresh tokens with 30-day expiry
- Device fingerprinting for security
- Concurrent session limits by role

## Technical Requirements

### Database Schema
```sql
-- Users table (Supabase Auth)auth.users (managed by Supabase)

-- Custom user profiles
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    user_type VARCHAR(50) NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    phone_verified BOOLEAN DEFAULT FALSE,
    profile_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### API Endpoints
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- POST /auth/refresh
- POST /auth/verify-email- POST /auth/verify-phone
- POST /auth/reset-password
- GET /auth/me
- PUT /auth/profile

### Security Requirements
- Bcrypt for password hashing
- Rate limiting on auth endpoints
- CAPTCHA on registration
- Email/SMS verification required
- Audit logging for all auth events

## UI/UX Requirements

### Registration Page
- Clean, mobile-first design
- Role selection with icons
- Progress indicator for multi-step
- Clear error messaging
- Social login options (Google, Apple)

### Login Page
- Email/phone input with validation
- Password field with show/hide toggle
- Remember me checkbox
- Forgot password link
- Magic link option

## Success Metrics
- Registration completion rate > 80%
- Login success rate > 95%
- Password reset completion > 70%
- Time to register < 2 minutes
- Zero security breaches
## Acceptance Criteria
- [ ] Property Manager can register and create organization
- [ ] Contractor can register with business details
- [ ] Email verification works within 5 minutes
- [ ] Login works with email and password
- [ ] Password reset sends email within 30 seconds
- [ ] Sessions persist across browser refresh
- [ ] Logout clears all session data
- [ ] Role-based redirects work correctly

## [NEEDS CLARIFICATION]
- Should we support social login providers?
- What MFA methods should we prioritize?
- Should contractors need approval before access?
- How many concurrent sessions per user?
- Should we track failed login attempts?

---
Status: DRAFT
Last Updated: 2025-01-17
Next Step: Technical planning