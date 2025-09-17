# Context Management Strategy

## 🧠 How Claude Maintains Context

### Files Claude Always Reads
1. **CLAUDE.md** (root) - Project state, always under 200 lines
2. **PROGRESS.md** - Current sprint status
3. **migrations/applied.md** - Database state

### How to Start Any New Session
```
"Continue InstaBids-Management project"
```
Claude will automatically:
- Read CLAUDE.md for project state
- Check PROGRESS.md for current work
- Look at migrations/applied.md for DB status
- Resume from "Next Actions" in CLAUDE.md

## 📁 Document Organization

### Permanent Reference (Rarely Changes)
```
docs/
├── VISION.md          # Why we're building
├── PAIN_POINTS.md     # Problems we solve
├── FEATURE_BREAKDOWN.md # What to build
├── DATABASE_SCHEMA.md # Complete DB design
├── TECH_STACK.md      # Technology choices
└── ROADMAP.md         # 12-week schedule
```

### Living Documents (Constantly Updated)
```
/
├── CLAUDE.md          # Current state (UPDATE AFTER EACH SESSION)
├── PROGRESS.md        # Sprint tracking (UPDATE DAILY)
└── migrations/
    └── applied.md     # DB migrations (UPDATE AFTER EACH MIGRATION)
```

### Feature Work (Created As Needed)
```
specs/
└── [feature-name]/
    ├── spec.md        # Business requirements
    ├── plan.md        # Technical design
    └── tasks.md       # Implementation tasks
```

## 🔄 Workflow to Maintain Context

### Starting a Feature
1. Check PROGRESS.md for what's next
2. Run `/specify [feature]` 
3. Update PROGRESS.md status
4. Update CLAUDE.md "In Progress"

### During Development
1. Complete tasks from `specs/[feature]/tasks.md`
2. Update PROGRESS.md with completed items
3. When applying DB changes, update `migrations/applied.md`

### Ending a Session
1. Update CLAUDE.md "Next Actions"
2. Update PROGRESS.md "Completed Today"
3. Commit with clear message

### Starting New Session
1. Say "Continue InstaBids-Management"
2. Claude reads context files
3. Continue from "Next Actions"

## 🗄️ Database Management

### Option 1: Track in Files (Recommended for Now)
- Keep all SQL in `migrations/` folder
- Update `applied.md` when you run them
- Can recreate database from files

### Option 2: Direct to Supabase (Later)
- Use MCP tools to apply directly
- Still update `applied.md` for tracking
- Better for production

## 📊 Avoiding Context Overload

### Keep Files Small
- CLAUDE.md < 200 lines
- PROGRESS.md < 150 lines  
- Each spec < 100 lines

### Archive Completed Work
```
archive/
└── completed/
    └── week1/
        └── user-auth/
```

### Use References, Not Copies
Instead of:
```markdown
The complete database schema is: [500 lines]
```

Do:
```markdown
Database schema: See docs/DATABASE_SCHEMA.md
```

## 🚫 Common Pitfalls to Avoid

### Don't:
- Put everything in CLAUDE.md (it gets too big)
- Forget to update tracking files
- Mix completed and pending work
- Store secrets in any file
- Create duplicate documentation

### Do:
- Keep CLAUDE.md focused on current state
- Update PROGRESS.md daily
- Archive completed features
- Use environment variables for secrets
- Reference docs instead of copying

## 🎯 Quick Reference Commands

### Check Project State
```
"What's the current state of InstaBids-Management?"
```
→ Claude reads CLAUDE.md and PROGRESS.md

### Resume Work
```
"Continue working on InstaBids-Management"
```
→ Claude picks up from "Next Actions"

### Apply Database Changes
```
"Apply migration 001 to Supabase"
```
→ Claude uses MCP tools and updates applied.md

### Start New Feature
```
"/specify [next feature from FEATURE_BREAKDOWN.md]"
```
→ Creates new spec and updates tracking

## 📈 Tracking What's Done

### Feature Level
- ✅ In CLAUDE.md "Completed Features"
- Move from "In Progress" to "Completed"

### Task Level  
- ✅ In PROGRESS.md daily updates
- Check off items as done

### Database Level
- ✅ In migrations/applied.md
- Move from "Pending" to "Applied"

## 💡 Best Practices

1. **One Feature at a Time**
   - Complete auth before starting properties
   - Reduces context needed

2. **Clear Commit Messages**
   ```
   Feature: User Auth - Added registration endpoint
   Progress: 3/25 tasks complete
   ```

3. **Regular Archives**
   - Weekly: Archive completed specs
   - Monthly: Clean up old progress

4. **Test Checkpoints**
   ```
   "Run test suite for user auth"
   "Verify database tables created"
   ```

## 🔗 The Golden Rule

**If it's important for the next session, it goes in CLAUDE.md**

Everything else lives in its proper place:
- Business info → docs/
- Current work → PROGRESS.md
- DB state → migrations/applied.md
- Feature details → specs/

---

This strategy keeps context manageable even as the project grows!