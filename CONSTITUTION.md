# InstaBids-Management Constitution

## Core Principles

### 1. Simplicity First
- Prefer direct solutions over abstractions
- No patterns without proven need  
- Start with the simplest working solution

### 2. Data Integrity
- All database operations must be transactional
- No data modifications without audit trails
- Backup before destructive operations

### 3. Security by Default
- All endpoints require authentication
- Input validation on every user input
- No sensitive data in logs or responses

### 4. Performance Standards
- API responses < 200ms (p95)
- Dashboard loads < 3 seconds
- Batch operations must show progress

### 5. User Experience
- Every action needs user feedback
- Destructive actions require confirmation
- Clear error messages with solutions

## Technical Constraints

- **Language**: Python 3.11+
- **Framework**: FastAPI for backend
- **Database**: PostgreSQL via Supabase
- **Frontend**: React with TypeScript
- **Testing**: pytest with 80% coverage minimum
- **Documentation**: All public APIs must have OpenAPI docs

## Forbidden Patterns
- No circular dependencies
- No god objects/modules
- No magic numbers/strings
- No silent failures
- No untested error paths

## Required Patterns
- Repository pattern for data access
- Service layer for business logic
- DTO/Models separation
- Centralized error handling
- Structured logging with context

---
*Version 1.0.0 - Created for InstaBids-Management project*