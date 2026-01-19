---
name: componentGen
description: Generates enterprise-grade React components with strict separation of concerns and accessibility default.
---

# Professional Component Generation Skill

## Philosophy
Components are the building blocks of the UI. They must be robust, typed, and accessible.

## File Structure Standard
`frontend/src/components/Feature/ComponentName/`
- `ComponentName.tsx`: **View Layer**. Purely presentational if possible.
- `useComponentName.ts`: **Logic Layer**. Custom hook for state/effects (if complex).
- `ComponentName.module.css` (or Tailwind): **Style Layer**.
- `ComponentName.test.tsx`: **Verification**.
- `index.ts`: **Public API**.

## Implementation Rules
1.  **Strict Typing**:
    - No `any`.
    - Define `interface Props` immediately.
    - Export shared types if reusable.

2.  **Logic Separation**:
    - If a component has >3 `useState` or `useEffect` hooks, extract them to `useComponentName.ts`.
    - The View (`.tsx`) should read like a declarative config.

3.  **Accessibility (a11y)**:
    - **Interactive Elements**: Must have keyboard handlers (`onKeyDown`) if they have `onClick`.
    - **Images**: Must have meaningful `alt` text.
    - **Forms**: inputs must have associated labels (`htmlFor` or nesting).

4.  **Performance**:
    - Use `useCallback` for event handlers passed to children.
    - Use `useMemo` for expensive derived calculations.

## Template (`ComponentName.tsx`)
```tsx
import { memo } from 'react';
import { useComponentName } from './useComponentName';
import classes from './ComponentName.module.css';

interface Props {
  id: string;
  onAction: (id: string) => void;
}

export const ComponentName = memo(({ id, onAction }: Props) => {
  const { data, isLoading } = useComponentName(id);

  if (isLoading) return <div role="status">Loading...</div>;

  return (
    <article className={classes.root}>
      <h1>{data.title}</h1>
      <button 
        onClick={() => onAction(id)}
        aria-label={`Action for ${data.title}`}
      >
        Go
      </button>
    </article>
  );
});
```
