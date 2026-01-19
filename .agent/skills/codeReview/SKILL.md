---
name: codeReview
description: Comprehensive code review checklist including SOLID, Security, and Performance standards.
---

# Professional Code Review Skill

Conduct a deep analysis of the code using these pillars.

## 1. Architecture & Design Principles
- **SOLID**:
    - **S**: Single Responsibility? (Does this class/function do too much?)
    - **O**: Open/Closed? (Can we extend without modifying?)
    - **L**: Liskov Substitution? (Do subclasses break the parent contract?)
    - **I**: Interface Segregation? (Are interfaces small and specific?)
    - **D**: Dependency Inversion? (Are high-level modules independent of low-level details?)
- **DRY**: Is code duplicated? Suggest refactoring to a utility or component.
- **KISS**: Is the solution over-engineered? Simplicity > Cleverness.

## 2. Security & Safety
- **Inputs**: Are all external inputs validated/sanitized?
- **Secrets**: Are keys/tokens hardcoded? (MUST use `.env`).
- **Data**: Is PII handled correctly?
- **Dependencies**: Are we introducing vulnerable packages?

## 3. Performance
- **Big O**: Are there nested loops on potential large datasets?
- **Database**:
    - N+1 queries?
    - Missing indexes?
    - Unnecessary full-table scans?
- **Frontend**:
    - Unnecessary re-renders?
    - Large bundle sizes (check imports)?

## 4. Code Quality & Style
- **Naming**: Do variables reveal intent? (`isUserLoggedIn` vs `flag`).
- **Comments**: Do they explain *WHY*, not *WHAT*?
- **Testing**:
    - Are edge cases covered?
    - Are failure modes tested?

## Feedback Format
"I noticed [X]. It might cause [Y]. Consider [Z] because [Reason]."