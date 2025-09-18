# 🤖 Codex Agent Onboarding: Project Creation Feature

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
/specs/project-creation/spec.md     # Complete feature specification
/specs/project-creation/plan.md     # Technical implementation plan
/specs/project-creation/tasks.md    # 96 detailed tasks to complete
```

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Ready Tables for Project Creation:**
- `projects` - Main project data
- `project_media` - Photos/videos
- `contractors` - Contractor profiles  
- `invitations` - Contractor invitations
- `smartscope_analyses` - AI project analysis
- `properties` - Property information
- `organizations` - Organization context
- `user_profiles` - User management

**Use These Tools:**
- `mcp__supabase__execute_sql` - Run SQL queries
- `mcp__supabase__apply_migration` - If you need new tables
- `mcp__supabase__list_tables` - Check what exists

## 🎯 **Your Mission: Project Creation Feature**

### **Goal**
Build a complete project creation system that enables property managers to create maintenance projects in <2 minutes and automatically match/invite qualified contractors.

### **Key Features to Build**
1. **Project Creation Wizard** - Multi-step form for project details
2. **Media Upload** - Photo/video upload for project documentation
3. **SmartScope Integration** - AI analysis of project photos
4. **Contractor Matching** - Algorithm to find qualified contractors
5. **Invitation System** - Automated contractor invitations
6. **Project Management** - CRUD operations for projects

### **Success Criteria**
- ✅ All 96 tasks in `tasks.md` completed
- ✅ Project creation API endpoints working
- ✅ Frontend wizard functional
- ✅ Contractor matching algorithm implemented
- ✅ Integration with SmartScope AI
- ✅ Database operations tested and verified

## 🔧 **Development Guidelines**

### **File Structure**
```
src/api/projects/               # Backend API endpoints
src/components/project-wizard/  # Frontend React components
tests/project-creation/         # Test files
```

### **Database Operations**
- **ALWAYS** use Supabase MCP tools for database work
- **NEVER** hardcode database credentials
- **TEST** every database operation with real data
- **UPDATE** `migrations/applied.md` if you create new tables

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/project-creation

# Commit frequently with descriptive messages
git commit -m "feat: implement project creation API endpoints"

# Update progress tracking
# Edit /PROGRESS.md after completing major milestones
```

### **Progress Tracking**
**ALWAYS update these files:**
- `/PROGRESS.md` - Mark features as complete
- `/specs/project-creation/tasks.md` - Check off completed tasks

## ⚠️ **Critical Integration Points**

### **External Systems**
- **Existing Campaign Logic** - You may need to integrate with existing contractor requirement logic
- **SmartScope AI** - Use `smartscope_analyses` table for AI project analysis
- **File Storage** - Implement media upload for project photos/videos

### **Shared Components**
- **Contractor Matching Algorithm** - Build this for project-creation, contractor-onboarding will use it
- **Invitation System** - Core to project workflow
- **File Upload Service** - Shared across multiple features

### **Dependencies**
- **Properties** - Projects must reference existing properties
- **User Authentication** - Projects created by authenticated property managers
- **Organizations** - Projects scoped to organization context

## 🚀 **Getting Started Checklist**

### **Phase 1: Setup & Understanding**
- [ ] Read all required files above
- [ ] Test Supabase connection with `mcp__supabase__list_tables`
- [ ] Review the 96 tasks in `tasks.md`
- [ ] Understand the project creation user flow in `spec.md`

### **Phase 2: Backend Development**
- [ ] Create project creation API endpoints
- [ ] Implement contractor matching algorithm
- [ ] Build invitation system
- [ ] Add media upload functionality
- [ ] Integrate SmartScope AI triggers

### **Phase 3: Frontend Development**
- [ ] Build project creation wizard UI
- [ ] Implement media upload interface
- [ ] Create project management dashboard
- [ ] Add contractor invitation interface

### **Phase 4: Integration & Testing**
- [ ] Test all API endpoints with real data
- [ ] Verify database operations work correctly
- [ ] Test contractor matching algorithm
- [ ] Validate SmartScope AI integration
- [ ] Update progress documentation

## 📞 **When to Ask Questions**

**STOP and ask before:**
- Modifying database schema (new tables/columns)
- Integrating with external contractor acquisition system
- Making major architectural decisions
- If you can't find information in the required reading

**Proceed independently with:**
- Building API endpoints per the specification
- Creating frontend components per the design
- Implementing business logic per the requirements
- Testing and validating functionality

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ Functional project creation in <2 minutes
- ✅ Automatic contractor matching and invitations
- ✅ SmartScope AI integration working
- ✅ All database operations tested and verified
- ✅ Clean, maintainable code following project conventions
- ✅ Updated progress tracking documentation

---

**Ready to start? Read the required files above, then dive into the 96 tasks in `tasks.md`!**