# Theme-Aware Logo Implementation Design

**Date:** 2025-12-28
**Status:** Approved
**Author:** Design Session

## Overview

Replace the placeholder text-based logo ("I" in colored box) in the TopHeader with actual logo files from the `public/` directory. Implement smart theme switching to display the appropriate logo variant based on the user's theme preference (light/dark mode).

## Goals

1. Use actual logo assets (`logo.svg` and `logo-dark.svg`) instead of placeholder
2. Automatically switch logos based on theme (light/dark mode)
3. Set up proper theme management system using `next-themes`
4. Maintain existing header layout and functionality
5. Provide smooth transitions when theme changes

## Architecture

### 1. Theme Provider Setup

**Location:** `src/main.tsx`

**Provider Hierarchy:**
```tsx
<StrictMode>
  <HelmetProvider>
    <ThemeProvider>          // New: Theme management
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  </HelmetProvider>
</StrictMode>
```

**ThemeProvider Configuration:**
- `attribute="class"` - Adds `dark` class to `<html>` for Tailwind dark mode
- `defaultTheme="system"` - Respects OS preference by default
- `enableSystem={true}` - Automatic OS theme detection
- `storageKey="iqx-theme"` - Persists theme in localStorage

**Benefits:**
- Users can choose: light, dark, or system (follows OS)
- Theme persists across sessions
- Seamless Tailwind dark mode integration
- Available throughout entire app

### 2. Theme-Aware Logo Component

**Location:** `src/components/ui/theme-aware-logo.tsx`

**Component Design:**
```tsx
interface ThemeAwareLogoProps {
  className?: string
  alt?: string
}

function ThemeAwareLogo({ className, alt = "IQX Logo" }: ThemeAwareLogoProps)
```

**Key Features:**
1. **Automatic Theme Detection**
   - Uses `useTheme()` hook from next-themes
   - Reads `resolvedTheme` to handle "system" theme properly
   - Resolves to actual "light" or "dark" value

2. **Smart Logo Selection**
   - Light mode: `/logo.svg`
   - Dark mode: `/logo-dark.svg`
   - Fallback: Light logo during hydration

3. **Smooth Transitions**
   - CSS transition on opacity (200ms)
   - Prevents jarring switches when theme changes

4. **Flexible & Reusable**
   - Accepts `className` for custom sizing
   - Accepts `alt` for accessibility
   - Can be used anywhere in the app

**Implementation Details:**
- Uses standard `<img>` tag for maximum compatibility
- Maintains aspect ratio with `w-auto`
- Handles SSR/hydration gracefully
- No layout shift during theme switch

### 3. TopHeader Integration

**File:** `src/components/dashboard/layout/TopHeader.tsx`

**Changes:**

**Before (lines 23-30):**
```tsx
<Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-bold text-lg">
    I
  </div>
  <span className="text-lg font-bold tracking-tight hidden md:block">
    IQX
  </span>
</Link>
```

**After:**
```tsx
<Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
  <ThemeAwareLogo className="h-8 w-auto" />
  <span className="text-lg font-bold tracking-tight hidden md:block">
    IQX
  </span>
</Link>
```

**Import Addition:**
```tsx
import { ThemeAwareLogo } from "@/components/ui/theme-aware-logo"
```

**Preserved Features:**
- Same height (`h-8` = 32px) matches header scale
- Maintains aspect ratio with `w-auto`
- Keeps hover effects and transitions
- Responsive text label behavior
- All existing menu and auth functionality

## Error Handling & Edge Cases

### Hydration Handling
- **Issue:** `resolvedTheme` may be undefined during SSR/initial render
- **Solution:** Default to light logo, switch smoothly once theme resolves
- **Result:** No flash of wrong logo, graceful fallback

### Missing Logo Files
- **Current State:** Logo files exist in `public/` directory
- **Fallback Strategy:** Browser shows broken image if files missing
- **Future Enhancement:** Could add error boundary or fallback to text logo

### Theme Switching Performance
- **Behavior:** Logo switches instantly on theme change
- **Visual Feedback:** 200ms CSS fade transition
- **Layout Stability:** No layout shift (logos maintain dimensions)

### Browser Compatibility
- Standard `<img>` tag - universal browser support
- CSS transitions - full modern browser support
- `useTheme` hook - handles server/client rendering properly

## Assets

**Logo Files in `public/`:**
- `logo.svg` - Light mode logo (1697 bytes)
- `logo-dark.svg` - Dark mode logo (2020 bytes)
- `logo-icon.svg` - Icon variant (1946 bytes, not used in this design)

**Verified:** All logo files exist and are ready to use.

## Implementation Plan

1. **Add ThemeProvider to main.tsx**
   - Wrap existing providers with ThemeProvider
   - Configure with proper attributes

2. **Create ThemeAwareLogo component**
   - New file: `src/components/ui/theme-aware-logo.tsx`
   - Implement theme detection logic
   - Add smooth transitions

3. **Update TopHeader component**
   - Import ThemeAwareLogo
   - Replace placeholder div with logo component
   - Test theme switching behavior

4. **Verification**
   - Test light/dark/system theme modes
   - Verify smooth transitions
   - Check responsive behavior
   - Confirm no layout shifts

## Benefits

1. **Professional Appearance** - Real logo instead of placeholder
2. **Better UX** - Logo matches theme automatically
3. **Future-Ready** - Theme system available for entire app
4. **Maintainable** - Reusable component for logo usage elsewhere
5. **No Breaking Changes** - All existing functionality preserved

## Future Enhancements

- Add theme toggle button in settings
- Extend theme system to other components
- Consider animated logo transitions
- Add logo-icon.svg for mobile/compact views
