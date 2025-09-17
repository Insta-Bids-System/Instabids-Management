# InstaBids-Management: Codex Agent Instructions

## 🎯 Project Context
**Marketplace Platform**: Property managers create maintenance projects, contractors submit quotes
**Database**: 21 tables in Supabase supporting complete marketplace workflow
**Status**: Database complete, 2 features done, 5 features ready for parallel development

## 🗄️ Required Database Connection

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**ALWAYS use these tools for database operations:**
- `mcp__supabase__execute_sql` - Run SQL queries (project_id: lmbpvkfcfhdfaihigfdu)
- `mcp__supabase__list_tables` - Check existing tables
- `mcp__supabase__apply_migration` - Only if new tables needed (rare)

**NEVER:**
- Hardcode database credentials
- Use raw SQL without MCP tools
- Modify existing table schemas without approval

## 📋 Required Reading (Read in Order)

### **Before Starting Any Feature:**
1. `/CLAUDE.md` - Complete project context and development guidelines
2. `/README.md` - Marketplace vision and technical overview
3. `/PROGRESS.md` - Current status and what's already built
4. `/specs/README.md` - Parallel development strategy and conflicts
5. `/migrations/applied.md` - Database migration status and history

### **For Your Specific Feature:**
6. `/specs/[your-feature]/AGENTS.md` - Feature-specific instructions (START HERE)
7. `/specs/[your-feature]/spec.md` - Complete feature requirements
8. `/specs/[your-feature]/plan.md` - Technical implementation plan (if exists)
9. `/specs/[your-feature]/tasks.md` - Detailed task breakdown

## 🔧 Development Rules

### **File Structure Standards**
```
src/api/[feature]/                 # Backend API endpoints
src/components/[feature]/          # Frontend React components
src/services/[feature]/            # Business logic and integrations
tests/[feature]/                   # Test files
```

### **Git Workflow (MANDATORY)**
```bash
# Always work on feature branches
git checkout -b feature/[feature-name]

# Commit frequently with descriptive messages
git commit -m "feat: implement [specific functionality]"
git commit -m "test: add [test description]"
git commit -m "fix: resolve [issue description]"

# Update progress tracking files
# Edit /PROGRESS.md after major milestones
```

### **Database Operations**
- **TEST EVERYTHING**: Verify all database operations with real data
- **READ-ONLY FIRST**: Test queries before any modifications
- **UPDATE TRACKING**: Update `/migrations/applied.md` if you create new tables

### **Code Standards**
- **TypeScript**: Use strict typing for all new code
- **React**: Use functional components with hooks
- **API**: Follow RESTful conventions
- **Error Handling**: Comprehensive error scenarios
- **Performance**: Optimize database queries and API responses

## 🧪 Testing Requirements (MANDATORY)

### **Before Claiming Feature Complete:**
1. **Unit Tests**: Test all functions individually
2. **Integration Tests**: Test complete workflows end-to-end
3. **Database Tests**: Verify all CRUD operations with real data
4. **API Tests**: Test all endpoints with various inputs
5. **Frontend Tests**: Validate UI components and user flows

### **Validation Commands**
```bash
# Run tests (if test framework exists)
npm test

# Check types (if TypeScript)
npx tsc --noEmit

# Lint code (if linter exists)
npm run lint

# Test database connection
# Use mcp__supabase__list_tables to verify connection
```

## ⚠️ When to STOP and Ask Questions

**STOP and ask before:**
- Modifying any existing database schema
- Making major architectural decisions
- Integrating with external systems (especially contractor acquisition)
- Adding new dependencies or services
- Changing authentication or organization logic

**Proceed independently with:**
- Building features per existing specifications
- Creating UI components per designs
- Implementing business logic per requirements
- Writing tests and documentation
- Optimizing performance

## 🔄 Progress Tracking (REQUIRED)

### **ALWAYS Update These Files:**
- `/PROGRESS.md` - Mark features and milestones as complete
- `/specs/[your-feature]/tasks.md` - Check off completed tasks
- `/migrations/applied.md` - If you create new database tables

### **Commit Messages Must Include:**
- What functionality was implemented
- What was tested and verified
- Any issues encountered and resolved

## 🚀 Integration Points

### **Shared Services (coordinate if building):**
- **Contractor Matching Algorithm** - Used by project-creation and contractor-onboarding
- **File Upload Service** - Used by multiple features for photos/documents
- **Notification System** - Cross-feature communication

### **External Systems (ask before integrating):**
- **External Contractor Acquisition System** - Recruits contractors via web search/email
- **OpenAI Vision API** - For SmartScope AI photo analysis
- **Email Processing** - For quote submission via email

## 📊 Success Criteria

### **Feature Complete Means:**
✅ All tasks in your feature's `tasks.md` completed
✅ All database operations tested with real data  
✅ All API endpoints functional and tested
✅ Frontend components working and responsive
✅ Integration with dependent features verified
✅ Error handling comprehensive
✅ Progress tracking files updated
✅ Code follows project conventions

### **Ready for Production Means:**
✅ Test coverage adequate for feature complexity
✅ Performance optimized (API responses < 500ms)
✅ Mobile responsiveness verified
✅ Security validation passed
✅ Documentation complete

## 🎯 Current Feature Status

### **✅ Complete (85-80%):**
- `user-authentication` - Needs testing and documentation
- `property-management` - Needs frontend UI components

### **🚧 Ready for Development:**
- `project-creation` - 96 tasks, contractor matching, auto-invitations
- `contractor-onboarding` - 75 tasks, verification workflow
- `quote-submission` - 60+ tasks, multi-format AI processing  
- `smartscope-ai` - 24 tasks, OpenAI Vision integration
- `admin-dashboard` - Analytics and reporting interface

---

**Start by reading your feature's `/specs/[feature]/AGENTS.md` file for feature-specific instructions, then dive into the task list!**