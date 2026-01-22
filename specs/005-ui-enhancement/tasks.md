# Tasks: TaskFlow UI Enhancement

**Input**: Design documents from `/specs/005-ui-enhancement/`
**Prerequisites**: plan.md, spec.md, research.md, design-tokens.md
**Branch**: `005-ui-enhancement`
**Date**: 2026-01-21

**Tests**: Visual testing only (manual verification + browser DevTools contrast checking). No automated tests for styling changes.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- All file paths relative to `frontend/`

## User Story Mapping

| Story | Priority | Title | Files Affected |
|-------|----------|-------|----------------|
| US1 | P1 | Visual Brand Impact | layout.tsx, page.tsx, globals.css |
| US2 | P1 | Immersive Background | page.tsx, globals.css, (auth)/layout.tsx |
| US3 | P2 | Interactive Button Feedback | button.tsx, globals.css, tailwind.config.ts |
| US4 | P2 | Cohesive Color Palette | globals.css |
| US5 | P3 | Typography Enhancement | globals.css, layout.tsx |

---

## Phase 1: Setup (Foundation Layer)

**Purpose**: Establish design tokens and font infrastructure without visual changes

**Risk**: LOW - No visual changes until Phase 2

- [x] T001 Document original CSS variable values as backup in `specs/005-ui-enhancement/design-tokens.md` (verify backup section exists)
- [x] T002 [P] Add Poppins font import using next/font/google in `frontend/app/layout.tsx`
- [x] T003 [P] Add `--font-brand` CSS custom property in `frontend/app/globals.css` (alongside existing --font-inter)
- [x] T004 [P] Add animation timing variables (--duration-fast, --duration-normal, --duration-slow) in `frontend/app/globals.css`
- [x] T005 [P] Add easing function variables (--ease-out, --ease-bounce) in `frontend/app/globals.css`

**Checkpoint**: Run `npm run dev` - application should load identically to before (no visual changes)

---

## Phase 2: Foundational (Shared Styling Infrastructure)

**Purpose**: Add new CSS classes and Tailwind utilities that user stories will use

**⚠️ CRITICAL**: These shared utilities must be complete before user story implementation

- [x] T006 Add `.brand-gradient` CSS class (light mode) in `frontend/app/globals.css`
- [x] T007 Add `.brand-gradient` CSS class (dark mode override) in `frontend/app/globals.css`
- [x] T008 [P] Add `.bg-gradient-main` utility class (light mode) in `frontend/app/globals.css`
- [x] T009 [P] Add `.bg-gradient-main` utility class (dark mode override) in `frontend/app/globals.css`
- [x] T010 Add button transition keyframes in `frontend/tailwind.config.ts`
- [x] T011 Add `prefers-reduced-motion` media query overrides in `frontend/app/globals.css`

**Checkpoint**: Classes defined but not yet applied. Run build to verify no syntax errors: `npm run build`

---

## Phase 3: User Story 1 - Visual Brand Impact (Priority: P1) 🎯 MVP

**Goal**: TaskFlow brand name displayed with distinctive premium font and gradient color

**Independent Test**: Visit landing page → TaskFlow name should have Poppins font with purple-to-pink gradient

### Verification Criteria

- [x] Brand name uses Poppins 700 (bold) font
- [x] Brand name displays gradient effect (purple-blue → magenta)
- [x] Gradient adapts properly in dark mode (purple → cyan)
- [x] Text scales appropriately on mobile (smaller but still prominent)

### Implementation for User Story 1

- [x] T012 [US1] Apply `font-brand` class to TaskFlow h1 in `frontend/app/page.tsx`
- [x] T013 [US1] Apply `.brand-gradient` class to TaskFlow h1 in `frontend/app/page.tsx`
- [x] T014 [US1] Add responsive font sizing for brand name in `frontend/app/page.tsx` (text-3xl sm:text-4xl md:text-5xl)
- [x] T015 [US1] Update header component brand text styling in `frontend/components/layout/header.tsx` (if brand appears there)
- [x] T016 [US1] Verify brand text in both light and dark modes

**Checkpoint**: TaskFlow brand name should be visually distinctive. All other UI unchanged.

---

## Phase 4: User Story 2 - Immersive Background (Priority: P1)

**Goal**: Attractive gradient background on landing page that enhances visual appeal without hurting readability

**Independent Test**: Visit landing page → See gradient background with smooth color transitions

### Verification Criteria

- [x] Landing page displays gradient background (not solid color)
- [x] Text remains readable over background (contrast ≥ 4.5:1)
- [x] Gradient adapts in dark mode
- [x] No layout shifts when background loads

### Implementation for User Story 2

- [x] T017 [US2] Apply `.bg-gradient-main` to main container in `frontend/app/page.tsx`
- [x] T018 [US2] Remove or update existing `bg-gradient-to-br` class if present in `frontend/app/page.tsx`
- [x] T019 [P] [US2] Apply gradient background to auth layout in `frontend/components/auth/auth-layout.tsx`
- [x] T020 [US2] Ensure card components have solid background for text readability in `frontend/app/page.tsx`
- [x] T021 [US2] Test background on mobile viewport (320px - 768px)
- [x] T022 [US2] Test background on desktop viewport (1024px+)

**Checkpoint**: Landing page and auth pages have attractive gradient. All text readable.

---

## Phase 5: User Story 3 - Interactive Button Feedback (Priority: P2)

**Goal**: All buttons display smooth hover effects with scale and shadow transitions

**Independent Test**: Hover over any button → Button should scale slightly and show shadow

### Verification Criteria

- [x] Primary buttons show scale + shadow on hover
- [x] Secondary/outline buttons show appropriate hover effect
- [x] Active/click state shows "pressed" feedback (scale down)
- [x] Animations respect prefers-reduced-motion preference
- [x] Transition duration is 200ms (smooth but responsive)

### Implementation for User Story 3

- [x] T023 [US3] Update primary button variant in `frontend/components/ui/button.tsx` with transition classes
- [x] T024 [US3] Add `hover:scale-[1.02]` to primary button variant in `frontend/components/ui/button.tsx`
- [x] T025 [US3] Add `hover:shadow-lg` to primary button variant in `frontend/components/ui/button.tsx`
- [x] T026 [US3] Add `active:scale-[0.98]` to primary button variant in `frontend/components/ui/button.tsx`
- [x] T027 [P] [US3] Update outline button variant with harmonious hover effect in `frontend/components/ui/button.tsx`
- [x] T028 [P] [US3] Update secondary button variant with harmonious hover effect in `frontend/components/ui/button.tsx`
- [x] T029 [P] [US3] Update ghost button variant with hover effect in `frontend/components/ui/button.tsx`
- [x] T030 [US3] Add `transition-all duration-200` to base button class in `frontend/components/ui/button.tsx`
- [x] T031 [US3] Test all button variants for hover effects (Get Started, Sign In, Add Task, etc.)
- [x] T032 [US3] Test with `prefers-reduced-motion: reduce` enabled in browser DevTools

**Checkpoint**: All buttons have smooth hover effects. Click any button to verify functionality not broken.

---

## Phase 6: User Story 4 - Cohesive Color Palette (Priority: P2)

**Goal**: Modern purple-blue primary color with coral accent throughout application

**Independent Test**: Navigate all pages → All UI elements use consistent color palette

### Verification Criteria

- [x] Primary color is vibrant purple-blue (not default blue)
- [x] Accent color is warm coral
- [x] Colors consistent on all pages (landing, auth, tasks)
- [x] Dark mode colors properly adjusted
- [x] All contrast ratios ≥ 4.5:1

### Implementation for User Story 4

- [x] T033 [US4] Update `--color-primary` light mode value in `frontend/app/globals.css` @theme block
- [x] T034 [US4] Update `--color-primary-foreground` light mode value in `frontend/app/globals.css`
- [x] T035 [P] [US4] Update `--color-secondary` light mode value in `frontend/app/globals.css`
- [x] T036 [P] [US4] Update `--color-accent` light mode value in `frontend/app/globals.css`
- [x] T037 [P] [US4] Update `--color-background` light mode value in `frontend/app/globals.css`
- [x] T038 [P] [US4] Update `--color-muted` and `--color-muted-foreground` light mode values in `frontend/app/globals.css`
- [x] T039 [P] [US4] Update `--color-border` and `--color-input` light mode values in `frontend/app/globals.css`
- [x] T040 [US4] Update `--color-primary` dark mode value in `frontend/app/globals.css` .dark block
- [x] T041 [US4] Update `--color-primary-foreground` dark mode value in `frontend/app/globals.css`
- [x] T042 [P] [US4] Update `--color-secondary` dark mode value in `frontend/app/globals.css`
- [x] T043 [P] [US4] Update `--color-accent` dark mode value in `frontend/app/globals.css`
- [x] T044 [P] [US4] Update `--color-background` dark mode value in `frontend/app/globals.css`
- [x] T045 [P] [US4] Update `--color-card` dark mode value in `frontend/app/globals.css`
- [x] T046 [P] [US4] Update `--color-muted` and `--color-muted-foreground` dark mode values in `frontend/app/globals.css`
- [x] T047 [US4] Verify contrast ratios with browser DevTools (Accessibility panel)
- [x] T048 [US4] Test theme toggle (light ↔ dark) for smooth transition

**Checkpoint**: Color palette applied consistently. Toggle light/dark to verify both themes work.

---

## Phase 7: User Story 5 - Typography Enhancement (Priority: P3)

**Goal**: Modern, readable typography with clear visual hierarchy

**Independent Test**: Read text on any page → Fonts should be clean, modern, well-spaced

### Verification Criteria

- [x] Body text is highly readable (Inter font, proper line-height)
- [x] Headings have clear hierarchy (different sizes/weights)
- [x] Font colors provide good contrast
- [x] No font loading flash (FOIT)

### Implementation for User Story 5

- [x] T049 [US5] Verify `font-feature-settings` in body CSS in `frontend/app/globals.css`
- [x] T050 [P] [US5] Ensure heading classes use appropriate font weights in `frontend/app/globals.css`
- [x] T051 [P] [US5] Add letter-spacing to brand text class in `frontend/app/globals.css`
- [x] T052 [US5] Verify font fallback chain includes system fonts in `frontend/app/layout.tsx`
- [x] T053 [US5] Test font loading with throttled network (DevTools → Network → Slow 3G)

**Checkpoint**: Typography is modern and readable. Test font fallback by blocking Google Fonts.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, accessibility compliance, and cleanup

- [x] T054 Run accessibility audit in Chrome DevTools (Lighthouse → Accessibility)
- [x] T055 Verify all WCAG 2.1 AA contrast requirements met
- [x] T056 [P] Test reduced-motion preference for all animations
- [x] T057 [P] Test on Chrome, Firefox, Safari browsers
- [x] T058 [P] Test responsive layout on mobile (375px), tablet (768px), desktop (1440px)
- [x] T059 [P] Verify no console errors during navigation
- [x] T060 Test complete user flows: signup → signin → create task → complete task → signout
- [x] T061 Update viewport meta themeColor in `frontend/app/layout.tsx` to match new palette
- [x] T062 Final visual comparison: light mode vs dark mode consistency

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
┌───────────────────────────────────────┐
│ Phase 3 (US1) ←→ Phase 4 (US2)        │  Can run in parallel (both P1)
│         ↓               ↓              │
│ Phase 5 (US3) ←→ Phase 6 (US4)        │  Can run in parallel (both P2)
│                   ↓                    │
│             Phase 7 (US5)              │  P3 - depends on US4 for colors
└───────────────────────────────────────┘
    ↓
Phase 8 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|------------|---------------------|
| US1 | Phase 2 | US2 |
| US2 | Phase 2 | US1 |
| US3 | Phase 2 | US4 |
| US4 | Phase 2 | US3 |
| US5 | US4 (for colors) | None |

### Within Each Phase

- Tasks marked [P] can run in parallel
- Tasks without [P] must complete before next task in that story

---

## Parallel Execution Examples

### Phase 1: All [P] tasks can run together

```bash
# Launch in parallel:
T002: Add Poppins font import in layout.tsx
T003: Add --font-brand CSS property in globals.css
T004: Add animation timing variables in globals.css
T005: Add easing function variables in globals.css
```

### Phase 3 + 4: Both P1 user stories can run in parallel

```bash
# Developer A works on US1 (Brand):
T012-T016: TaskFlow brand styling

# Developer B works on US2 (Background):
T017-T022: Background gradient implementation
```

### Phase 5: Button variants can parallelize

```bash
# Launch in parallel:
T027: Update outline button variant
T028: Update secondary button variant
T029: Update ghost button variant
```

### Phase 6: Color updates within same file (sequence), but light/dark can overlap

```bash
# Sequence for light mode:
T033 → T034 → T035 → T036 → T037 → T038 → T039

# Then dark mode:
T040 → T041 → T042 → T043 → T044 → T045 → T046
```

---

## Implementation Strategy

### MVP (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011)
3. Complete Phase 3: US1 - Brand Impact (T012-T016)
4. Complete Phase 4: US2 - Background (T017-T022)
5. **STOP and VALIDATE**: Verify brand and background work
6. Demo MVP to stakeholders

**MVP Delivers**: Distinctive TaskFlow branding + attractive gradient background

### Full Implementation

1. MVP steps above
2. Add Phase 5: US3 - Button Interactions (T023-T032)
3. Add Phase 6: US4 - Color Palette (T033-T048)
4. Add Phase 7: US5 - Typography (T049-T053)
5. Complete Phase 8: Polish (T054-T062)

### Verification Checklist (After Each Phase)

- [ ] Application loads without console errors
- [ ] All existing functionality works (create/edit/delete tasks)
- [ ] Authentication flow works (signin/signup/signout)
- [ ] Theme toggle works (light/dark)
- [ ] Mobile responsive layout intact
- [ ] No layout shifts or flickering

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 62 |
| **Setup Tasks** | 5 |
| **Foundational Tasks** | 6 |
| **US1 Tasks (P1)** | 5 |
| **US2 Tasks (P1)** | 6 |
| **US3 Tasks (P2)** | 10 |
| **US4 Tasks (P2)** | 16 |
| **US5 Tasks (P3)** | 5 |
| **Polish Tasks** | 9 |
| **Parallel Opportunities** | 28 tasks marked [P] |
| **MVP Scope** | Phases 1-4 (22 tasks) |

---

## Notes

- All changes are additive to minimize risk to existing functionality
- CSS variable names are preserved; only values change
- Rollback reference available in `design-tokens.md`
- Color values from `design-tokens.md` - use exact HSL values specified
- Test after each phase checkpoint before proceeding
