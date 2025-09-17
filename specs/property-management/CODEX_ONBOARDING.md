# 🤖 Codex Agent Onboarding: Property Management Feature

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
/migrations/003_property_management.sql # Property management schema
```

### **4. Feature Requirements (THIS FEATURE)**
```
/specs/property-management/spec.md     # Complete feature specification
/specs/property-management/plan.md     # Technical implementation plan
/specs/property-management/tasks.md    # 136 detailed tasks (80% complete)
```

## ✅ **FEATURE STATUS: 80% COMPLETE**

### **What's Already Built:**
- ✅ Database tables (properties, property_groups, property_group_members, property_audit_log)
- ✅ Backend API (14 endpoints, full CRUD, import/export)
- ✅ Property management business logic
- ✅ Geocoding and mapping integration
- ✅ Property grouping and organization

### **What's Remaining:**
- [ ] Frontend UI components (property list, detail pages)
- [ ] Property import/export interface
- [ ] Property search and filtering
- [ ] Mobile responsiveness

## 🗄️ **Database Connection**

**Supabase Configuration:**
```yaml
Project ID: lmbpvkfcfhdfaihigfdu
URL: https://lmbpvkfcfhdfaihigfdu.supabase.co
Environment: Development
```

**Property Management Tables (Already Created):**
- `properties` - Main property information with geocoding
- `property_groups` - Property organization and grouping
- `property_group_members` - Group membership relationships
- `property_audit_log` - Property change tracking
- `organizations` - Property ownership context

## 🎯 **Your Mission: Complete Property Management Frontend**

### **Goal**
Build the remaining frontend components to complete the property management system, focusing on user interface and user experience.

### **Remaining Features to Build**
1. **Property List View** - Searchable, filterable property listing
2. **Property Detail Pages** - Comprehensive property information display
3. **Property Creation/Edit Forms** - User-friendly property management interface
4. **Import/Export Interface** - Bulk property operations
5. **Property Groups Management** - Group creation and member management
6. **Mobile-Responsive Design** - Optimized for mobile property managers

### **Success Criteria**
- ✅ Complete the remaining 20% of tasks in `tasks.md`
- ✅ Intuitive property management interface
- ✅ Fast, responsive property search and filtering
- ✅ Bulk import/export functionality working
- ✅ Mobile-optimized design
- ✅ Integration with existing backend API

## 🔧 **Development Guidelines**

### **Existing File Structure**
```
src/api/properties/                # Backend API endpoints (COMPLETE)
src/components/properties/         # Frontend components (NEEDS WORK)
tests/property-management/         # Test files (NEEDS COMPLETION)
```

### **Database Operations**
- **ALREADY WORKING** - All property tables and APIs are complete
- **USE EXISTING ENDPOINTS** - 14 backend endpoints are ready to use
- **NO SCHEMA CHANGES** - Focus on frontend development

### **Git Workflow**
```bash
# Work on feature branch
git checkout -b feature/property-frontend

# Focus on UI components and user experience
git commit -m "feat: implement property list view with search and filters"

# Update progress tracking
# Edit /PROGRESS.md when tasks are complete
```

### **Progress Tracking**
**ALWAYS update these files:**
- `/PROGRESS.md` - Mark features as complete
- `/specs/property-management/tasks.md` - Check off completed frontend tasks

## ⚠️ **Critical Integration Points**

### **Existing Backend API**
- **14 Endpoints Ready** - Full CRUD, search, import/export APIs available
- **Property Groups** - Management API for property organization
- **Geocoding** - Address validation and mapping coordinates
- **Audit Logging** - Property change tracking

### **Frontend Requirements**
- **React Components** - Build reusable property management components
- **Responsive Design** - Mobile-first approach for property managers in the field
- **State Management** - Handle property data and user interactions
- **File Upload** - For property photos and document import

### **Dependencies**
- **User Authentication** - Property managers need to be logged in
- **Organization Context** - Properties scoped to user's organization
- **File Storage** - Property photos and documents

## 🚀 **Getting Started Checklist**

### **Phase 1: Setup & Understanding**
- [ ] Read all required files above
- [ ] Test existing backend API endpoints
- [ ] Review the remaining frontend tasks in `tasks.md`
- [ ] Understand the property data model and relationships

### **Phase 2: Core UI Components**
- [ ] Build property list view with search and filtering
- [ ] Create property detail/view page
- [ ] Implement property creation and editing forms
- [ ] Add property photo upload and management

### **Phase 3: Advanced Features**
- [ ] Build property groups management interface
- [ ] Implement bulk import/export UI
- [ ] Add property mapping and geocoding display
- [ ] Create property audit log viewer

### **Phase 4: Polish & Testing**
- [ ] Optimize for mobile responsiveness
- [ ] Add comprehensive form validation
- [ ] Test all UI components thoroughly
- [ ] Update progress to 100% complete

## 📞 **When to Ask Questions**

**STOP and ask before:**
- Making any database schema changes (shouldn't be needed)
- Modifying existing backend API endpoints
- Adding new property data fields or structures
- Changing property grouping or organization logic

**Proceed independently with:**
- Building React components for property management
- Creating user interfaces per the specification
- Implementing frontend search and filtering
- Adding responsive design and mobile optimization

## 🔄 **Relationship to Other Features**

### **Foundation For:**
- **Project Creation** - Projects are created for specific properties
- **Contractor Matching** - Contractors matched based on property location
- **Admin Dashboard** - Property metrics and analytics

### **Integrates With:**
- **User Authentication** - Property managers access their properties
- **Organizations** - Properties belong to specific organizations
- **File Storage** - Property photos and documents

## 📱 **Frontend Design Requirements**

### **Property List View**
- [ ] Searchable property list with real-time filtering
- [ ] Property cards with key information (address, type, status)
- [ ] Sorting options (name, date, type, status)
- [ ] Bulk selection and operations
- [ ] Pagination for large property portfolios

### **Property Detail View**
- [ ] Comprehensive property information display
- [ ] Photo gallery with upload functionality
- [ ] Property history and audit log
- [ ] Quick actions (edit, duplicate, archive)
- [ ] Integration with mapping services

### **Property Forms**
- [ ] Step-by-step property creation wizard
- [ ] Address validation and geocoding
- [ ] Property type and amenity selection
- [ ] Photo upload with drag-and-drop
- [ ] Form validation and error handling

### **Mobile Optimization**
- [ ] Touch-friendly interface for field property managers
- [ ] Offline capability for property viewing
- [ ] GPS integration for location-based features
- [ ] Fast loading and responsive design

## 🎉 **Success Metrics**

When you're done, you should have:
- ✅ Complete property management user interface
- ✅ Fast, intuitive property search and filtering
- ✅ Bulk property import/export functionality
- ✅ Mobile-optimized design for field use
- ✅ Property groups management interface
- ✅ Integration with all existing backend APIs
- ✅ Comprehensive testing of all UI components
- ✅ Updated progress tracking to 100% complete

---

**Ready to complete this feature? Read the required files above, test the existing backend API, then build the remaining frontend components to finish the property management system!**