---
description: Create or update the feature specification from a natural language feature description.
---

# /specify Command

Given the feature description provided, do this:

1. Load `.specify/templates/spec-template.md` to understand required sections
2. Write the specification using the template structure, replacing placeholders with concrete details derived from the feature description while preserving section order and headings
3. Save to `specs/[feature-name]/spec.md`
4. Report completion and readiness for the next phase

When creating a spec:
- Mark all ambiguities with [NEEDS CLARIFICATION: specific question]
- Focus on WHAT users need and WHY
- Avoid HOW to implement (no tech stack, APIs, code structure)
- Write for business stakeholders, not developers