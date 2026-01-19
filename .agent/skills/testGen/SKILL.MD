---
name: testGen
description: Detailed testing strategy enforcing AAA pattern, edge case coverage, and continuous validation.
---

# Professional Test Generation Skill

Tests are the specification of the system. They must be trustworthy.

## 1. The AAA Pattern
All tests must follow the structure:
- **Arrange**: Set up the state (mock data, render component).
- **Act**: Execute the specific function/interaction.
- **Assert**: Verify the result.

## 2. What to Test
- **Happy Path**: Does it work when everything is correct?
- **Edge Cases**: Empty lists, null values, network errors, huge numbers.
- **Security**: Can a user access unauthorized data? (Integration tests).

## 3. Backend (Pytest)
`backend/tests/`
- **Fixtures**: Use `conftest.py` for shared DB setup. DONT repeat setup code.
- **Isolation**: Each test must start with a clean state.
- **Mocking**: Mock external APIs (Spotify API). Do NOT hit real endpoints in tests.

## 4. Frontend (React Testing Library)
`src/components/Feature/ComponentName.test.tsx`
- **User-Centric**: Find elements by role (`screen.getByRole('button', {name: 'Save'})`), not CSS class.
- **Async**: Use `waitFor` for state updates.
- **Snapshots**: Use sparingly. They are fragile. Explicit assertions are better.

## 5. Definition of Done
A feature is not done until:
1.  A test exists.
2.  The test fails (Red) - optional but recommended.
3.   The test passes (Green).
4.  Linter passes.
