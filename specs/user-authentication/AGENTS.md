# 🤖 Codex Agent Onboarding: User Authentication Feature

## 📖 **Required Reading (Read in Order)**

### **1. Project Foundation (MUST READ FIRST)**
```
/CLAUDE.md                           # Core project context, database config, development rules
/README.md                          # Project overview and marketplace vision
/PROGRESS.md                        # Current status, what's built, what's next
```

### **2. Development Strategy**
```
/specs/README.md                    # Parallel development strategy, feature conflicts
```

### **3. Database Foundation**
```
/migrations/applied.md              # Track what's in Supabase, migration history
```

### **4. Feature Requirements (THIS FEATURE)**
```
/specs/user-authentication/spec.md     # Complete feature specification
/specs/user-authentication/plan.md     # Technical implementation plan
/specs/user-authentication/tasks.md    # Detailed tasks (85% complete)
```

## ✅ **FEATURE STATUS: 85% COMPLETE**

### **What's Already Built:**
- ✅ Database tables and auth system (Supabase Auth + custom profiles)
- ✅ Backend API (9 endpoints, JWT tokens, rate limiting)
- ✅ Frontend components (login/register forms)
- ✅ User profile management
- ✅ Organization context and role-based permissions

### **What's Remaining:**
- [ ] Testing and validation
- [ ] Error handling improvements
- [ ] Documentation completion
- [ ] Performance optimization

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Authentication Tables (Already Created):**
- `user_profiles` - Extended user information
- `organizations` - Organization context
- `auth_audit_log` - Authentication audit trail
- `user_sessions` - Session management
- `password_history` - Password change tracking

## 🎯 **Your Mission: Complete User Authentication**

### **Goal**
Finish the remaining 15% of the user authentication system by adding comprehensive testing, error handling, and documentation.

### **Remaining Tasks**
1. **Testing Suite** - Unit tests for all auth endpoints
2. **Integration Testing** - End-to-end auth flow validation
3. **Error Handling** - Comprehensive error scenarios and responses
4. **Documentation** - API documentation and user guides
5. **Performance** - Optimize auth queries and response times

## 🔧 **Development Guidelines**

### **Existing File Structure**
```
src/api/auth/                      # Backend auth endpoints (COMPLETE)
src/components/auth/               # Frontend auth components (COMPLETE)
tests/auth/                        # Test files (NEEDS WORK)
docs/api/auth/                     # API documentation (NEEDS CREATION)
```

### **Database Operations**
- **ALREADY WORKING** - All auth tables and RLS policies are complete
- **TEST THOROUGHLY** - Verify all existing functionality works
- **NO SCHEMA CHANGES** - Focus on testing and optimization

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/auth-completion

# Focus on testing and documentation
git commit -m "test: add comprehensive auth test suite"

# Update progress tracking
# Edit /PROGRESS.md when 100% complete
```

## ⚠️ **Critical Integration Points**

### **Existing Integrations**
- **All Features** - Every other feature depends on user authentication
- **Supabase Auth** - Integrated with Supabase built-in authentication
- **Organization Context** - Users belong to organizations (property managers)
- **Role-Based Access** - Admin, manager, contractor role permissions

### **Testing Requirements**
- **Unit Tests** - Test all auth functions individually
- **Integration Tests** - Test complete auth flows
- **Security Testing** - Validate JWT tokens, rate limiting, permissions
- **Performance Testing** - Auth response time optimization

## 🚀 **Getting Started Checklist**

### **Phase 1: Assessment**
- [ ] Read all required files above
- [ ] Test existing auth system thoroughly
- [ ] Identify gaps in current implementation
- [ ] Review the remaining tasks in `tasks.md`

### **Phase 2: Testing Implementation**
- [ ] Create comprehensive unit test suite
- [ ] Build integration tests for auth flows
- [ ] Add security validation tests
- [ ] Test error scenarios and edge cases

### **Phase 3: Documentation & Polish**
- [ ] Create API documentation for all auth endpoints
- [ ] Write user guides for authentication flows
- [ ] Optimize performance and response times
- [ ] Add comprehensive error handling

### **Phase 4: Validation & Completion**
- [ ] Run full test suite and validate 100% pass rate
- [ ] Test integration with other platform features
- [ ] Verify security and performance requirements
- [ ] Update progress to 100% complete

## 📞 **When to Ask Questions**

**STOP and ask before:**
- Making any database schema changes (shouldn't be needed)
- Modifying existing auth architecture
- Adding new authentication methods or providers
- Changing organization or role structures

**Proceed independently with:**
- Writing comprehensive tests for existing functionality
- Creating documentation for existing API endpoints
- Optimizing performance of existing code
- Adding error handling improvements

## 🔄 **Relationship to Other Features**

### **Enables All Other Features:**
- **Project Creation** - Requires authenticated property managers
- **Contractor Onboarding** - Requires contractor user accounts
- **Quote Submission** - Requires authenticated contractors
- **Admin Dashboard** - Requires admin user permissions
- **Property Management** - Requires organization context

### **Security Foundation:**
- **JWT Tokens** - Secure API access for all features
- **Rate Limiting** - Protection against abuse
- **Role-Based Access** - Permissions for different user types
- **Audit Logging** - Security monitoring and compliance

## 🧪 **Testing Requirements**

### **Unit Tests**
- [ ] Registration endpoint validation
- [ ] Login flow and JWT generation
- [ ] Password reset functionality
- [ ] User profile management
- [ ] Organization context handling

### **Integration Tests**
- [ ] Complete user registration to project creation flow
- [ ] Contractor registration to quote submission flow
- [ ] Admin login to dashboard access flow
- [ ] Cross-organization security validation

### **Security Tests**
- [ ] JWT token validation and expiry
- [ ] Rate limiting functionality
- [ ] SQL injection prevention
- [ ] Cross-site scripting (XSS) protection
- [ ] Role-based access control validation

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ 100% test coverage for all authentication functionality
- ✅ Comprehensive API documentation
- ✅ Robust error handling for all edge cases
- ✅ Optimized performance (auth responses < 200ms)
- ✅ Security validation and penetration testing passed
- ✅ Integration with all other platform features verified
- ✅ Updated progress tracking to 100% complete

---

**Ready to finish this feature? Read the required files above, test the existing system thoroughly, then complete the remaining testing and documentation tasks!**