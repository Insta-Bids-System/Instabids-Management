# 🤖 Codex Agent Onboarding: Admin Dashboard Feature

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
/specs/admin-dashboard/spec.md      # Complete feature specification
```

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Available Tables for Analytics (Read-Only):**
- `organizations` - Organization metrics
- `user_profiles` - User activity and growth
- `properties` - Property management stats
- `projects` - Project creation and completion metrics
- `contractors` - Contractor onboarding and performance
- `quotes` - Quote submission and conversion rates
- `awards` - Contract awards and completion
- `invitations` - Invitation and response rates
- `smartscope_analyses` - AI analysis performance
- `project_media` - Media upload statistics

**Use These Tools:**
- `mcp__supabase__execute_sql` - Run read-only SQL queries
- `mcp__supabase__list_tables` - Check what exists

## 🎯 **Your Mission: Admin Dashboard Feature**

### **Goal**
Build a comprehensive analytics and monitoring dashboard for InstaBids platform administrators to track system performance, user engagement, and business metrics.

### **Key Features to Build**
1. **System Overview** - High-level platform health and activity metrics
2. **User Analytics** - Property manager and contractor growth and engagement
3. **Project Metrics** - Project creation, completion, and success rates
4. **Financial Dashboard** - Quote volumes, contract values, and revenue tracking
5. **Performance Monitoring** - AI accuracy, response times, system health
6. **Reporting Tools** - Exportable reports and data visualization

### **Success Criteria**
- ✅ Comprehensive dashboard with all key business metrics
- ✅ Real-time data visualization and analytics
- ✅ User-friendly interface with intuitive navigation
- ✅ Exportable reports and data insights
- ✅ Performance monitoring and alerting
- ✅ Role-based access control for admin users

## 🔧 **Development Guidelines**

### **File Structure**
```
src/api/admin/                     # Backend analytics API endpoints
src/components/admin-dashboard/    # Frontend dashboard components
src/components/charts/             # Reusable chart components
src/services/analytics/            # Data processing and aggregation
tests/admin-dashboard/             # Test files
```

### **Database Operations**
- **ALWAYS** use Supabase MCP tools for database work
- **READ-ONLY** operations only - no data modification
- **NEVER** hardcode database credentials
- **OPTIMIZE** queries for performance with large datasets

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/admin-dashboard

# Commit frequently with descriptive messages
git commit -m "feat: implement project metrics dashboard with charts"

# Update progress tracking
# Edit /PROGRESS.md after completing major milestones
```

### **Progress Tracking**
**ALWAYS update these files:**
- `/PROGRESS.md` - Mark features as complete
- Create `/specs/admin-dashboard/tasks.md` - Track your implementation tasks

## ⚠️ **Critical Integration Points**

### **Data Sources**
- **All Database Tables** - Read-only access to complete platform data
- **Real-time Updates** - Consider WebSocket integration for live data
- **Historical Trends** - Time-series analysis of platform growth

### **Visualization Libraries**
- **Chart.js** or **D3.js** - For interactive data visualization
- **React Dashboard Libraries** - For layout and components
- **Export Tools** - PDF/Excel export functionality

### **Performance Considerations**
- **Query Optimization** - Efficient aggregation queries
- **Caching Strategy** - Cache expensive analytics calculations
- **Pagination** - Handle large datasets appropriately

### **Dependencies**
- **User Authentication** - Admin-only access control
- **All Platform Features** - Dashboard consumes data from entire system

## 🚀 **Getting Started Checklist**

### **Phase 1: Setup & Understanding**
- [ ] Read all required files above
- [ ] Test Supabase connection with `mcp__supabase__list_tables`
- [ ] Explore database schema and understand data relationships
- [ ] Create comprehensive task list for dashboard features

### **Phase 2: Backend Analytics API**
- [ ] Create analytics aggregation endpoints
- [ ] Implement user metrics calculations
- [ ] Build project and contractor analytics
- [ ] Add financial metrics and reporting
- [ ] Optimize query performance

### **Phase 3: Frontend Dashboard**
- [ ] Design dashboard layout and navigation
- [ ] Build interactive charts and visualizations
- [ ] Implement real-time data updates
- [ ] Add filtering and date range selection
- [ ] Create exportable report functionality

### **Phase 4: Advanced Features**
- [ ] Add performance monitoring and alerting
- [ ] Implement role-based access control
- [ ] Create custom report builder
- [ ] Add data export and scheduling
- [ ] Update progress documentation

## 📞 **When to Ask Questions**

**STOP and ask before:**
- Modifying database schema (should not be needed)
- Making major architectural decisions about data caching
- Implementing user role and permission systems
- Setting up external analytics integrations

**Proceed independently with:**
- Building read-only analytics API endpoints
- Creating dashboard UI components and charts
- Implementing data visualization features
- Testing and validating dashboard functionality

## 🔄 **Relationship to Other Features**

### **Consumes Data From:**
- **All Features** - Dashboard shows metrics from entire platform
- **User Authentication** - User growth and engagement metrics
- **Project Creation** - Project volume and success rates
- **Contractor Onboarding** - Contractor growth and verification rates
- **Quote Submission** - Quote volumes and conversion metrics
- **SmartScope AI** - AI performance and accuracy metrics

### **Independent Operation:**
- **100% Read-Only** - No impact on other feature development
- **Reporting Focus** - Analytics and insights rather than operational features

## 📊 **Key Metrics to Track**

### **Platform Overview**
- Total users, properties, projects, contractors
- Active users (daily, weekly, monthly)
- Platform growth rates and trends

### **User Engagement**
- Property manager activity and project creation rates
- Contractor registration and profile completion
- User retention and churn analysis

### **Business Metrics**
- Project success rates and completion times
- Quote submission and acceptance rates
- Contract values and revenue tracking
- Geographic distribution and market penetration

### **Performance Metrics**
- SmartScope AI accuracy and confidence scores
- System response times and uptime
- Error rates and issue tracking

### **Financial Analytics**
- Revenue per customer and lifetime value
- Cost per acquisition and conversion rates
- Quote-to-contract conversion ratios

## 🎨 **Dashboard Design Principles**

### **User Experience**
- **Clean Interface** - Minimal, focused design
- **Intuitive Navigation** - Easy access to key metrics
- **Responsive Design** - Works on desktop and mobile
- **Fast Loading** - Optimized for performance

### **Data Visualization**
- **Interactive Charts** - Drill-down capabilities
- **Real-time Updates** - Live data where appropriate
- **Export Functionality** - PDF and Excel export options
- **Customizable Views** - Personalized dashboard layouts

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ Comprehensive admin dashboard with all key platform metrics
- ✅ Interactive data visualization and analytics
- ✅ Fast, responsive interface with excellent UX
- ✅ Exportable reports and data insights
- ✅ Real-time monitoring and alerting capabilities
- ✅ All database operations optimized for performance
- ✅ Clean, maintainable code following project conventions
- ✅ Updated progress tracking documentation

---

**Ready to start? Read the required files above, explore the database schema, then create your implementation plan! This feature is 100% independent - perfect for parallel development.**