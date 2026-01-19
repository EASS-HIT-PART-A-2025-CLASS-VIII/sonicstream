---
name: gitCommit
description: Standards for professional, semantic, and traceable commit history.
---

# Professional Git Commit Skill

A professional commit log is a historical document. Treat it with respect.

## 1. The Golden Rule
**One logical change = One commit.**
Do not mix "Fixing login bug" with "Refactoring CSS". Split them.

## 2. Message Format
```text
<type>(<scope>): <short summary>

<detailed description explaining WHY, not just WHAT>

[Footer(s)]
```

### Types
- `feat`: New feature for the user
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semi-colons, etc.
- `refactor`: Production code change that doesn't fix a bug
- `perf`: code change that improves performance
- `test`: Adding missing tests
- `chore`: Maintenance (build, tools)

### Rules
- **Imperative Mood**: "Add feature" not "Added feature".
- **No Periodic Saves**: "wip", "save", "temp" are FORBIDDEN on shared branches. Squash them locally.
- **Reference Issues**: If a ticket exists, link it. `Fixes #123`.

## 3. Workflow
1.  **Diff First**: `git diff` - Know exactly what you are staging.
2.  **Stage**: `git add -p` (patch mode) is recommended to review chunks.
3.  **Commit**: Write the message.
4.  **Verify**: `git show HEAD` - Did you include a debug print statement? Remove it.
