---
description: Generate an ordered, actionable task list from the implementation plan
---

# /tasks Command

Given the implementation plan, do this:

1. Load the plan from `specs/[feature-name]/plan.md`
2. Generate numbered tasks following this pattern:
   - Contract tests first (TDD approach)
   - Models/entities creation
   - Service layer implementation  
   - API/UI implementation
   - Integration tests
3. Mark tasks that can be done in parallel with [P]
4. Save ordered task list to `specs/[feature-name]/tasks.md`
5. Each task should be specific and actionable:
   - "Create User model with email validation"
   - "Write contract test for POST /api/users"
   - "Implement password reset service"

Target: 25-30 specific, ordered tasks ready for execution.