# 🤖 Codex Agent Onboarding: Contractor Onboarding Feature

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
/migrations/004_marketplace_core.sql # Database schema (21 tables ready)
```

### **4. Feature Requirements (THIS FEATURE)**
```
/specs/contractor-onboarding/spec.md     # Complete feature specification
/specs/contractor-onboarding/plan.md     # Technical implementation plan
/specs/contractor-onboarding/tasks.md    # 75 detailed tasks to complete
```

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Ready Tables for Contractor Onboarding:**
- `contractors` - Main contractor profiles
- `contractor_credentials` - Licenses, insurance, certifications
- `contractor_availability` - Work schedules and capacity
- `contractor_portfolio` - Work samples and testimonials
- `invitations` - Project invitations received
- `quotes` - Quote submissions
- `awards` - Contract awards and performance
- `user_profiles` - User authentication context

**Use These Tools:**
- `mcp__supabase__execute_sql` - Run SQL queries
- `mcp__supabase__apply_migration` - If you need new tables
- `mcp__supabase__list_tables` - Check what exists

## 🎯 **Your Mission: Contractor Onboarding Feature**

### **Goal**
Build a comprehensive contractor onboarding system that enables contractors to register, get verified, and set up profiles for automatic job matching.

### **⚠️ CRITICAL INTEGRATION NOTE**
**STOP AND ASK FIRST:** There is a separate external contractor acquisition system that actively recruits contractors via web search, email, and phone outreach. This feature may need to integrate with that external system instead of building standalone registration. **Check with Justin before implementing the registration flow.**

### **Key Features to Build**
1. **Registration Flow** - Multi-step contractor registration wizard
2. **Verification System** - License and insurance verification workflow
3. **Profile Management** - Comprehensive contractor profiles
4. **Portfolio Builder** - Work samples and testimonials
5. **Availability Settings** - Service areas and work schedules
6. **Integration Hub** - Connect with project invitations and quotes

### **Success Criteria**
- ✅ All 75 tasks in `tasks.md` completed
- ✅ Contractor registration/profile API endpoints working
- ✅ Verification workflow functional
- ✅ Portfolio and availability management
- ✅ Integration with project invitation system
- ✅ External system integration (if applicable)

## 🔧 **Development Guidelines**

### **File Structure**
```
src/api/contractors/               # Backend API endpoints
src/components/contractor-wizard/  # Frontend React components
src/components/contractor-profile/ # Profile management UI
tests/contractor-onboarding/       # Test files
```

### **Database Operations**
- **ALWAYS** use Supabase MCP tools for database work
- **NEVER** hardcode database credentials
- **TEST** every database operation with real data
- **UPDATE** `migrations/applied.md` if you create new tables

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/contractor-onboarding

# Commit frequently with descriptive messages
git commit -m "feat: implement contractor registration API"

# Update progress tracking
# Edit /PROGRESS.md after completing major milestones
```

### **Progress Tracking**
**ALWAYS update these files:**
- `/PROGRESS.md` - Mark features as complete
- `/specs/contractor-onboarding/tasks.md` - Check off completed tasks

## ⚠️ **Critical Integration Points**

### **External Systems**
- **External Contractor Acquisition System** - May replace the registration flow entirely
- **Project Invitation System** - Contractors receive and respond to project invitations
- **Verification Services** - May need to integrate with license/insurance validation APIs

### **Shared Components**
- **Contractor Matching Algorithm** - Built in project-creation, use it here for profile optimization
- **File Upload Service** - For credentials, portfolio images, documents
- **Notification System** - For verification status updates, project invitations

### **Dependencies**
- **User Authentication** - Contractors need user accounts
- **Project Creation** - Contractors respond to projects created by property managers
- **Quote Submission** - Contractors submit quotes for projects they're invited to

## 🚀 **Getting Started Checklist**

### **Phase 1: Setup & Understanding**
- [ ] Read all required files above
- [ ] **ASK ABOUT EXTERNAL SYSTEM INTEGRATION** before starting
- [ ] Test Supabase connection with `mcp__supabase__list_tables`
- [ ] Review the 75 tasks in `tasks.md`
- [ ] Understand the contractor onboarding flow in `spec.md`

### **Phase 2: Backend Development**
- [ ] Create contractor registration API endpoints
- [ ] Implement verification workflow
- [ ] Build profile management system
- [ ] Add portfolio and credential management
- [ ] Integrate with invitation system

### **Phase 3: Frontend Development**
- [ ] Build contractor registration wizard UI
- [ ] Create verification workflow interface
- [ ] Implement profile management dashboard
- [ ] Add portfolio builder interface
- [ ] Create availability settings UI

### **Phase 4: Integration & Testing**
- [ ] Test all API endpoints with real data
- [ ] Verify database operations work correctly
- [ ] Test integration with project invitations
- [ ] Validate verification workflow
- [ ] Update progress documentation

## 📞 **When to Ask Questions**

**STOP and ask before:**
- **Starting any registration flow implementation** (external system may handle this)
- Modifying database schema (new tables/columns)
- Integrating with verification services
- Making major architectural decisions about contractor acquisition

**Proceed independently with:**
- Building profile management per the specification
- Creating portfolio and credential interfaces
- Implementing availability and service area settings
- Testing and validating functionality (once architecture is confirmed)

## 🔄 **Relationship to Other Features**

### **Depends On:**
- **User Authentication** - Contractors need authenticated accounts
- **Project Creation** - Source of project invitations

### **Feeds Into:**
- **Quote Submission** - Contractors submit quotes for projects
- **Awards System** - Track contractor performance over time

### **Shared With:**
- **Contractor Matching Algorithm** - Used by project-creation for finding contractors
- **File Upload Service** - Used by multiple features for document/image uploads

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ Streamlined contractor onboarding process
- ✅ Comprehensive verification workflow
- ✅ Rich contractor profiles with portfolios
- ✅ Integration with project invitation system
- ✅ External system integration (if applicable)
- ✅ All database operations tested and verified
- ✅ Clean, maintainable code following project conventions
- ✅ Updated progress tracking documentation

---

**Ready to start? Read the required files above, then CHECK ABOUT EXTERNAL SYSTEM INTEGRATION before diving into the 75 tasks in `tasks.md`!**