# 🤖 Codex Agent Onboarding: Quote Submission Feature

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
/specs/quote-submission/spec.md     # Complete feature specification
/specs/quote-submission/tasks.md    # 60+ detailed tasks to complete
```

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Ready Tables for Quote Submission:**
- `quotes` - Main quote submissions
- `quote_line_items` - Detailed price breakdowns
- `projects` - Projects being quoted
- `contractors` - Contractor submitting quotes
- `awards` - Awarded contracts
- `project_media` - Project photos for reference
- `invitations` - Project invitations context

**Use These Tools:**
- `mcp__supabase__execute_sql` - Run SQL queries
- `mcp__supabase__apply_migration` - If you need new tables
- `mcp__supabase__list_tables` - Check what exists

## 🎯 **Your Mission: Quote Submission Feature**

### **Goal**
Build a multi-format quote submission system that enables contractors to submit quotes via PDF, email, photo, or web form, with AI-powered standardization achieving 85% accuracy.

### **Key Features to Build**
1. **Multi-Format Upload** - PDF, email, photo, web form quote submission
2. **AI Standardization** - Extract and standardize quote data using AI
3. **Quote Management** - CRUD operations for quotes and line items
4. **Version Control** - Handle quote updates and revisions
5. **Comparison Tools** - Enable property managers to compare quotes
6. **Integration Hub** - Connect with projects, contractors, and awards

### **Success Criteria**
- ✅ All 60+ tasks in `tasks.md` completed
- ✅ Multi-format quote upload working (PDF, email, photo, web form)
- ✅ AI standardization achieving 85% accuracy target
- ✅ Quote comparison and management interface
- ✅ Version control for quote updates
- ✅ Integration with project and contractor systems

## 🔧 **Development Guidelines**

### **File Structure**
```
src/api/quotes/                    # Backend API endpoints
src/components/quote-upload/       # Multi-format upload UI
src/components/quote-comparison/   # Quote comparison interface
src/services/ai-standardization/  # AI processing service
tests/quote-submission/            # Test files
```

### **Database Operations**
- **ALWAYS** use Supabase MCP tools for database work
- **NEVER** hardcode database credentials
- **TEST** every database operation with real data
- **UPDATE** `migrations/applied.md` if you create new tables

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/quote-submission

# Commit frequently with descriptive messages
git commit -m "feat: implement PDF quote processing with AI extraction"

# Update progress tracking
# Edit /PROGRESS.md after completing major milestones
```

### **Progress Tracking**
**ALWAYS update these files:**
- `/PROGRESS.md` - Mark features as complete
- `/specs/quote-submission/tasks.md` - Check off completed tasks

## ⚠️ **Critical Integration Points**

### **AI Services**
- **OpenAI Vision API** - For photo quote processing
- **Document AI** - For PDF text extraction
- **Standardization Engine** - Custom AI for data normalization

### **File Processing**
- **File Upload Service** - Handle PDF, photo uploads
- **Email Integration** - Process quotes sent via email
- **Image Processing** - OCR and vision analysis for photos

### **Business Logic**
- **Quote Comparison** - Algorithm for quote standardization and comparison
- **Version Control** - Handle quote updates and revision tracking
- **Validation Rules** - Business rules for quote acceptance

### **Dependencies**
- **Projects** - Quotes must reference active projects
- **Contractors** - Quotes submitted by verified contractors
- **Invitations** - Quotes typically respond to project invitations

## 🚀 **Getting Started Checklist**

### **Phase 1: Setup & Understanding**
- [ ] Read all required files above
- [ ] Test Supabase connection with `mcp__supabase__list_tables`
- [ ] Review the 60+ tasks in `tasks.md`
- [ ] Understand the quote submission flow in `spec.md`
- [ ] Set up AI service connections (OpenAI, etc.)

### **Phase 2: Backend Development**
- [ ] Create quote submission API endpoints
- [ ] Implement multi-format file processing
- [ ] Build AI standardization service
- [ ] Add quote management CRUD operations
- [ ] Implement version control system

### **Phase 3: Frontend Development**
- [ ] Build multi-format upload interface
- [ ] Create quote management dashboard
- [ ] Implement quote comparison tools
- [ ] Add quote editing and updating UI
- [ ] Create contractor quote submission portal

### **Phase 4: AI Integration & Testing**
- [ ] Test AI standardization accuracy
- [ ] Validate multi-format processing
- [ ] Test quote comparison algorithms
- [ ] Verify version control functionality
- [ ] Update progress documentation

## 📞 **When to Ask Questions**

**STOP and ask before:**
- Modifying database schema (new tables/columns)
- Making major AI service choices or configurations
- Implementing email integration architecture
- Making decisions about file storage solutions

**Proceed independently with:**
- Building quote submission API per the specification
- Creating upload interfaces per the design
- Implementing AI processing workflows
- Testing and validating functionality

## 🔄 **Relationship to Other Features**

### **Depends On:**
- **Projects** - Source of projects to quote
- **Contractors** - Contractors submit quotes
- **Invitations** - Quotes often respond to invitations

### **Feeds Into:**
- **Awards System** - Winning quotes become awarded contracts
- **Admin Dashboard** - Quote analytics and reporting

### **Independent From:**
- **SmartScope AI** - Different AI workflow
- **Property Management** - Minimal interaction
- **User Authentication** - Uses existing auth

## 🎯 **AI Accuracy Targets**

### **Quote Standardization Goals**
- **85% accuracy** for data extraction from all formats
- **Labor costs** extracted with 90% accuracy
- **Material costs** extracted with 85% accuracy
- **Timeline estimates** extracted with 80% accuracy
- **Line item breakdown** achieved for 75% of quotes

### **Processing Performance**
- **PDF processing** < 30 seconds
- **Photo processing** < 60 seconds
- **Email processing** < 45 seconds
- **Web form** instant processing

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ Multi-format quote submission working flawlessly
- ✅ AI standardization meeting 85% accuracy target
- ✅ Intuitive quote comparison interface
- ✅ Robust version control and quote management
- ✅ Seamless integration with project and contractor systems
- ✅ All database operations tested and verified
- ✅ Clean, maintainable code following project conventions
- ✅ Updated progress tracking documentation

---

**Ready to start? Read the required files above, then dive into the 60+ tasks in `tasks.md`!**