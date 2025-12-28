# Theme-Aware Logo Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace placeholder logo with theme-aware logo that automatically switches between light/dark variants based on user's theme preference.

**Architecture:** Add ThemeProvider wrapper to main.tsx using next-themes, create reusable ThemeAwareLogo component that detects current theme and renders appropriate logo, integrate into TopHeader component.

**Tech Stack:** React 19, TypeScript, next-themes, Vite, Tailwind CSS

---

## Task 1: Add ThemeProvider to Application Root

**Files:**
- Modify: `dashboard/src/main.tsx:1-18`

**Step 1: Add next-themes import**

Add import at top of file after existing imports:

```typescript
import { ThemeProvider } from 'next-themes'
```

**Step 2: Wrap App with ThemeProvider**

Modify the render tree (lines 9-17) to wrap ThemeProvider around AuthProvider:

```typescript
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HelmetProvider>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        storageKey="iqx-theme"
      >
        <AuthProvider>
          <App />
        </AuthProvider>
      </ThemeProvider>
    </HelmetProvider>
  </StrictMode>,
)
```

**Step 3: Verify ThemeProvider setup**

Run: `npm run dev`
Expected: App runs without errors, no console warnings

Open browser DevTools and check:
- localStorage should be accessible (will store theme preference)
- No React errors in console
- `<html>` tag should have class attribute support

**Step 4: Test theme class application**

Open browser console and run:
```javascript
document.documentElement.classList.add('dark')
```

Expected: HTML element should accept dark class (Tailwind dark mode setup)

**Step 5: Commit ThemeProvider setup**

```bash
git add dashboard/src/main.tsx
git commit -m "feat: add ThemeProvider for theme management

Set up next-themes ThemeProvider in application root to enable
theme switching throughout the app. Configured with class attribute
for Tailwind dark mode, system theme detection, and localStorage
persistence."
```

---

## Task 2: Create ThemeAwareLogo Component

**Files:**
- Create: `dashboard/src/components/ui/theme-aware-logo.tsx`

**Step 1: Create component file**

Create new file with imports and type definitions:

```typescript
import { useTheme } from "next-themes"
import { useEffect, useState } from "react"

interface ThemeAwareLogoProps {
  className?: string
  alt?: string
}
```

**Step 2: Implement ThemeAwareLogo component**

Add the component implementation:

```typescript
export function ThemeAwareLogo({
  className = "",
  alt = "IQX Logo"
}: ThemeAwareLogoProps) {
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Prevent hydration mismatch by waiting for client-side mount
  useEffect(() => {
    setMounted(true)
  }, [])

  // During SSR or before mount, use light logo as default
  const logoSrc = mounted && resolvedTheme === "dark"
    ? "/logo-dark.svg"
    : "/logo.svg"

  return (
    <img
      src={logoSrc}
      alt={alt}
      className={`transition-opacity duration-200 ${className}`}
    />
  )
}
```

**Step 3: Verify component structure**

Run TypeScript check:
```bash
cd dashboard && npx tsc --noEmit
```

Expected: No TypeScript errors

**Step 4: Test component in isolation (manual)**

Temporarily add to App.tsx for testing (will remove after):

```typescript
import { ThemeAwareLogo } from "./components/ui/theme-aware-logo"

// In App component, add temporarily:
<div className="p-4">
  <ThemeAwareLogo className="h-20 w-auto" />
</div>
```

Run: `npm run dev`
Expected: Logo appears on page

Test theme switching in console:
```javascript
document.documentElement.classList.toggle('dark')
```
Expected: Logo should switch between light and dark versions

Remove test code from App.tsx after verification.

**Step 5: Commit ThemeAwareLogo component**

```bash
git add dashboard/src/components/ui/theme-aware-logo.tsx
git commit -m "feat: create ThemeAwareLogo component

Add reusable component that automatically switches between logo.svg
and logo-dark.svg based on current theme. Handles SSR hydration
gracefully with mounted state. Includes smooth transition effect."
```

---

## Task 3: Update UI Components Index (Optional)

**Files:**
- Modify: `dashboard/src/components/ui/index.ts` (if exists, otherwise skip)

**Step 1: Check if index file exists**

Run: `ls dashboard/src/components/ui/index.ts`

If file exists, proceed to Step 2.
If file doesn't exist, skip to Task 4.

**Step 2: Add export to index file**

Add export at the end of the file:

```typescript
export { ThemeAwareLogo } from "./theme-aware-logo"
```

**Step 3: Commit index update**

```bash
git add dashboard/src/components/ui/index.ts
git commit -m "chore: export ThemeAwareLogo from ui components index"
```

---

## Task 4: Integrate ThemeAwareLogo into TopHeader

**Files:**
- Modify: `dashboard/src/components/dashboard/layout/TopHeader.tsx:1-30`

**Step 1: Add ThemeAwareLogo import**

Add import after existing imports (after line 6):

```typescript
import { ThemeAwareLogo } from "@/components/ui/theme-aware-logo";
```

**Step 2: Replace placeholder logo with ThemeAwareLogo**

Replace lines 23-30 (the Link with placeholder logo) with:

```typescript
<Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
    <ThemeAwareLogo className="h-8 w-auto" />
    <span className="text-lg font-bold tracking-tight hidden md:block">
        IQX
    </span>
</Link>
```

**Step 3: Verify TypeScript compilation**

Run: `cd dashboard && npx tsc --noEmit`
Expected: No TypeScript errors

**Step 4: Test in development**

Run: `npm run dev`
Expected:
- Logo appears in header
- Logo maintains proper size (32px height)
- Logo aspect ratio is preserved
- Hover effects work on link

**Step 5: Test theme switching**

In browser console, toggle dark mode:
```javascript
document.documentElement.classList.toggle('dark')
```

Expected:
- Logo switches between light and dark variants
- Transition is smooth (200ms fade)
- No layout shift occurs
- No console errors

**Step 6: Test responsive behavior**

Resize browser window to mobile size (< 768px).
Expected:
- Logo still appears
- "IQX" text label hides (hidden md:block)
- Layout remains stable

**Step 7: Commit TopHeader integration**

```bash
git add dashboard/src/components/dashboard/layout/TopHeader.tsx
git commit -m "feat: integrate ThemeAwareLogo into TopHeader

Replace placeholder text-based logo with actual logo component.
Logo now automatically switches between light/dark variants based
on theme. Maintains existing layout, hover effects, and responsive
behavior."
```

---

## Task 5: Production Build Verification

**Files:**
- N/A (testing task)

**Step 1: Run production build**

```bash
cd dashboard && npm run build
```

Expected: Build completes successfully with no errors

Check output for:
- No TypeScript errors
- No missing module errors
- Build artifacts created in `dist/` directory

**Step 2: Preview production build**

```bash
npm run preview
```

Expected: Preview server starts successfully

**Step 3: Test in preview mode**

Open preview URL (usually http://localhost:4173)

Test checklist:
- [ ] Logo appears in header
- [ ] Logo has correct size and spacing
- [ ] Theme switching works (use browser DevTools to toggle dark class)
- [ ] No console errors
- [ ] No broken image icons
- [ ] Smooth transitions between themes
- [ ] Mobile responsive view works

**Step 4: Check logo file paths in build**

Verify logos are included in build:
```bash
ls -la dashboard/dist/logo*.svg
```

Expected: logo.svg and logo-dark.svg are present in dist directory

**Step 5: Document completion**

If all tests pass, the implementation is complete. No commit needed (testing only).

---

## Task 6: Final Cleanup and Documentation

**Files:**
- Modify: `dashboard/README.md` (if theme switching should be documented)

**Step 1: Update README with theme information (optional)**

If README has a features section, add:

```markdown
### Theme Support
- Automatic light/dark mode based on system preferences
- Manual theme switching support via ThemeProvider
- Theme-aware logo that adapts to current theme
```

**Step 2: Commit README update (if applicable)**

```bash
git add dashboard/README.md
git commit -m "docs: add theme support to README"
```

**Step 3: Final verification checklist**

Verify all acceptance criteria:
- [x] ThemeProvider is properly configured in main.tsx
- [x] ThemeAwareLogo component created and working
- [x] TopHeader uses new logo component
- [x] Logo switches between light/dark themes
- [x] No layout shifts or visual glitches
- [x] Production build works correctly
- [x] All commits have descriptive messages

**Step 4: Push changes (when ready)**

```bash
git log --oneline
```

Review commit history, then push to remote (if applicable):
```bash
git push origin <branch-name>
```

---

## Acceptance Criteria

- [ ] ThemeProvider wraps application in main.tsx
- [ ] Theme persists in localStorage as "iqx-theme"
- [ ] ThemeAwareLogo component exists and exports properly
- [ ] Component handles SSR/hydration without errors
- [ ] Logo switches between logo.svg (light) and logo-dark.svg (dark)
- [ ] TopHeader displays logo instead of placeholder
- [ ] Logo maintains h-8 (32px) height with auto width
- [ ] Hover effects on logo link work correctly
- [ ] No TypeScript errors in codebase
- [ ] Production build succeeds
- [ ] No console errors or warnings
- [ ] Smooth 200ms transition when theme changes
- [ ] Responsive behavior preserved (mobile/desktop)

---

## Rollback Plan

If issues occur, rollback commits in reverse order:

```bash
# View commit history
git log --oneline

# Rollback to before theme implementation
git revert <commit-hash> --no-edit

# Or reset to previous state (destructive)
git reset --hard <commit-before-changes>
```

---

## Future Enhancements

- Add theme toggle button in user settings menu
- Consider animated logo transitions (fade + scale)
- Add logo-icon.svg support for compact mobile view
- Implement theme preference in user profile (backend sync)
- Add keyboard shortcut for theme toggle (e.g., Ctrl+Shift+T)
