# 🤖 Codex Agent Onboarding: SmartScope AI Feature

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
/specs/smartscope-ai/spec.md        # Complete feature specification
/specs/smartscope-ai/tasks.md       # 24 detailed tasks to complete
```

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Ready Tables for SmartScope AI:**
- `smartscope_analyses` - AI analysis results and metadata
- `projects` - Projects being analyzed
- `project_media` - Input photos and videos
- `contractors` - Recommended contractor trades
- `quotes` - Integration with quote submission

**Use These Tools:**
- `mcp__supabase__execute_sql` - Run SQL queries
- `mcp__supabase__apply_migration` - If you need new tables
- `mcp__supabase__list_tables` - Check what exists

## 🎯 **Your Mission: SmartScope AI Feature**

### **Goal**
Build an AI-powered project analysis system using OpenAI Vision that analyzes photos to extract project scope, recommend trades, and generate detailed requirements with 92% confidence targeting.

### **🔧 Parallel Development Approach**
**This feature can be split into 4 parallel submodules:**

1. **Photo Analysis Pipeline** - Image preprocessing, AI request handling, scope generation
2. **Domain Configuration** - Analysis categories, detailed prompting strategy  
3. **Scope Enhancement** - Human review UI, learning feedback, scope standardization
4. **Cross-cutting Safeguards** - Business logic, accuracy/performance targets, API management, security, cost tracking

### **Key Features to Build**
1. **Image Analysis** - OpenAI Vision API integration for photo analysis
2. **Scope Extraction** - AI-powered project scope and requirements extraction
3. **Trade Recommendation** - Intelligent contractor trade matching
4. **Confidence Scoring** - 92% confidence targeting with accuracy metrics
5. **Learning System** - Feedback loop for AI improvement
6. **Integration Hub** - Connect with project creation and contractor matching

### **Success Criteria**
- ✅ All 24 tasks in `tasks.md` completed
- ✅ OpenAI Vision integration working flawlessly
- ✅ 92% confidence targeting achieved
- ✅ Accurate trade recommendations
- ✅ Learning feedback system operational
- ✅ Integration with project creation workflow

## 🔧 **Development Guidelines**

### **File Structure**
```
src/api/smartscope/                # Backend AI processing endpoints
src/services/openai-vision/        # OpenAI Vision API integration
src/components/analysis-ui/        # Analysis results and review interface
src/services/learning-feedback/    # AI improvement system
tests/smartscope-ai/              # Test files
```

### **Database Operations**
- **ALWAYS** use Supabase MCP tools for database work
- **NEVER** hardcode database credentials or API keys
- **TEST** every AI analysis with real photo data
- **UPDATE** `migrations/applied.md` if you create new tables

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/smartscope-ai

# Commit frequently with descriptive messages
git commit -m "feat: implement OpenAI Vision photo analysis pipeline"

# Update progress tracking
# Edit /PROGRESS.md after completing major milestones
```

### **Progress Tracking**
**ALWAYS update these files:**
- `/PROGRESS.md` - Mark features as complete
- `/specs/smartscope-ai/tasks.md` - Check off completed tasks

## ⚠️ **Critical Integration Points**

### **AI Services**
- **OpenAI Vision API** - Primary image analysis engine
- **Custom Prompting Strategy** - Domain-specific construction/maintenance prompts
- **Confidence Scoring** - Accuracy measurement and targeting

### **Learning System**
- **Human Review Interface** - Property managers validate AI analysis
- **Feedback Loop** - Improve AI accuracy over time
- **Performance Tracking** - Monitor confidence scores and accuracy

### **Business Integration**
- **Project Creation** - Triggered automatically when projects are created
- **Contractor Matching** - AI recommends specific trades needed
- **Quote Comparison** - Analysis helps validate quote accuracy

### **Dependencies**
- **Projects** - Analysis triggered by project creation
- **Project Media** - Requires photos/videos to analyze
- **OpenAI API Key** - Required for Vision API access

## 🚀 **Getting Started Checklist**

### **Phase 1: Setup & Understanding**
- [ ] Read all required files above
- [ ] Test Supabase connection with `mcp__supabase__list_tables`
- [ ] Review the 24 tasks in `tasks.md`
- [ ] Understand the SmartScope AI workflow in `spec.md`
- [ ] Set up OpenAI Vision API access

### **Phase 2: Core AI Pipeline**
- [ ] Create OpenAI Vision API integration
- [ ] Implement image preprocessing
- [ ] Build scope extraction algorithms
- [ ] Add trade recommendation logic
- [ ] Implement confidence scoring

### **Phase 3: Learning & Enhancement**
- [ ] Build human review interface
- [ ] Implement feedback collection system
- [ ] Add learning algorithm for AI improvement
- [ ] Create performance monitoring dashboard

### **Phase 4: Integration & Testing**
- [ ] Test AI analysis with real construction photos
- [ ] Validate 92% confidence targeting
- [ ] Test integration with project creation
- [ ] Verify learning feedback loop
- [ ] Update progress documentation

## 📞 **When to Ask Questions**

**STOP and ask before:**
- Modifying database schema (new tables/columns)
- Making major OpenAI API configuration decisions
- Implementing learning algorithm architecture
- Setting up cost tracking and API rate limiting

**Proceed independently with:**
- Building OpenAI Vision integration per the specification
- Creating analysis UI components per the design
- Implementing confidence scoring algorithms
- Testing and validating AI accuracy

## 🔄 **Relationship to Other Features**

### **Triggers From:**
- **Project Creation** - Auto-analyzes project photos when projects are created
- **Manual Analysis** - Property managers can request ad-hoc analysis

### **Feeds Into:**
- **Contractor Matching** - AI trade recommendations improve matching
- **Quote Validation** - Analysis helps validate quote accuracy and completeness
- **Project Requirements** - Enhanced project specifications

### **Independent From:**
- **Quote Submission** - Separate AI workflow
- **Contractor Onboarding** - No direct interaction
- **Admin Dashboard** - May consume analysis data for reporting

## 🎯 **AI Performance Targets**

### **Accuracy Goals**
- **92% confidence** for scope extraction
- **Trade recommendations** 95% accuracy
- **Material identification** 85% accuracy
- **Issue detection** 90% accuracy
- **Cost estimation** 80% accuracy range

### **Performance Metrics**
- **Analysis time** < 30 seconds per photo
- **API cost** < $0.50 per analysis
- **Confidence improvement** 2% per month with feedback
- **User satisfaction** 4.5/5 rating on analysis quality

## 🤖 **OpenAI Vision Integration**

### **Required Setup**
```bash
# Environment variables needed
OPENAI_API_KEY=your_openai_api_key
SMARTSCOPE_MODEL=gpt-4-vision-preview
```

### **API Usage Pattern**
1. **Image Preprocessing** - Resize, optimize for Vision API
2. **Structured Prompting** - Domain-specific construction prompts
3. **Response Processing** - Extract structured data from AI response
4. **Confidence Calculation** - Assess AI confidence in analysis
5. **Result Storage** - Save to `smartscope_analyses` table

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ OpenAI Vision integration delivering 92% confidence
- ✅ Accurate trade recommendations and scope extraction
- ✅ Functional learning system improving AI over time
- ✅ Seamless integration with project creation workflow
- ✅ Cost-effective API usage with monitoring
- ✅ All database operations tested and verified
- ✅ Clean, maintainable code following project conventions
- ✅ Updated progress tracking documentation

---

**Ready to start? Read the required files above, then dive into the 24 tasks in `tasks.md`! This feature is 100% independent - perfect for parallel development.**