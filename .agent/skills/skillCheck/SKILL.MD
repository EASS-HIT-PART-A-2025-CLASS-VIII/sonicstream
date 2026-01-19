---
name: skillCheck
description: The Principal Engineer's checklist. Use this to audit ANY new skill or architectural decision.
---

# Skill Verification Skill (Meta-Skill)

Before marking ANY task as "Done", run it through this gauntlet.

## 1. The "Principal" Criteria
A solution is not professional unless it answers "YES" to all:

### Scalability
- [ ] **Data Volume**: Will this choke on 1 million records? (e.g., `SELECT *` vs Pagination).
- [ ] **Concurrency**: What happens if 1000 users hit this at once? (Locking strategies).

### Resilience (The "Anti-Fragile" Check)
- [ ] **Failure Mode**: When it breaks, does it crash the app (Fail Open) or just degrade (Fail Safe)?
- [ ] **Timeouts**: Are external calls bounded? (Never infinite wait).
- [ ] **Fallbacks**: If the "smart" thing fails, is there a "dumb" backup?

### Observability
- [ ] **Black Box**: Can I diagnose a bug *without* looking at the code? (Logs/Traces).
- [ ] **Explainability**: Does the system explain *why* it made a decision?

### Maintainability (SOLID)
- [ ] **Extension**: Can I add a new type/feature without modifying existing files? (Open/Closed).
- [ ] **Decoupling**: Are business rules separate from Infrastructure (DB/API)?

## 2. Usage
When creating/refining a skill or feature:
1.  Simulate a "Design Review" using this checklist.
2.  If any check fails, **Refactor immediately**.
3.  Only then is it "Professional".
