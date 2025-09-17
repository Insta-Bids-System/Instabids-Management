---
description: Define a technical implementation plan based on the feature specification
---

# /plan Command

Given the feature specification, do this:

1. Load the spec from `specs/[feature-name]/spec.md`
2. Load `.specify/templates/plan-template.md` 
3. Fill out the implementation plan with:
   - Technical context and architecture decisions
   - Research needs (Phase 0)
   - Design artifacts needed (Phase 1)
   - Task planning approach (Phase 2 - describe only, don't execute)
4. Save to `specs/[feature-name]/plan.md`
5. Create research.md, data-model.md, quickstart.md, and contracts/ as specified
6. Report completion and readiness for /tasks command

Remember: The /plan command stops at planning. It doesn't create tasks.md - that's for /tasks.