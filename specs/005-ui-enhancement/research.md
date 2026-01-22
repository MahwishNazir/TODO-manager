# Research: TaskFlow UI Enhancement

**Feature**: 005-ui-enhancement
**Date**: 2026-01-21
**Status**: Complete

## Research Questions

### 1. Brand Font Selection

**Question**: Which display font best represents TaskFlow's modern, professional identity?

**Research**:
- Evaluated popular display fonts: Poppins, Montserrat, Outfit, Space Grotesk
- Criteria: Modern aesthetic, high readability, good weight options, Google Fonts availability

**Decision**: **Poppins**
- Geometric sans-serif with friendly, modern feel
- Excellent bold weight (700) for brand names
- Pairs well with Inter (current body font)
- Wide language support
- Already widely used in modern SaaS applications

**Alternatives Rejected**:
- Montserrat: Slightly dated, overused
- Outfit: Less distinctive at large sizes
- Space Grotesk: Too technical/developer-focused

### 2. Color Palette Strategy

**Question**: What color scheme creates a modern, vibrant feel while maintaining accessibility?

**Research**:
- Analyzed current palette: Blue-based (#0070E0 primary), LinkedIn-inspired
- Modern trends: Gradients, vibrant purples, warm accent colors
- Accessibility requirement: WCAG 2.1 AA (4.5:1 contrast minimum)

**Decision**: **Blue-Purple Primary with Coral Accent**

Light Mode:
- Primary: `hsl(250, 100%, 60%)` - Vibrant purple-blue
- Accent: `hsl(15, 90%, 60%)` - Warm coral for highlights
- Background: `hsl(240, 20%, 98%)` - Soft off-white with slight blue tint
- Foreground: `hsl(240, 10%, 10%)` - Near black for text

Dark Mode:
- Primary: `hsl(250, 100%, 70%)` - Lighter purple-blue
- Accent: `hsl(15, 85%, 65%)` - Adjusted coral
- Background: `hsl(240, 30%, 8%)` - Deep navy
- Foreground: `hsl(240, 10%, 95%)` - Off-white text

**Rationale**:
- Purple-blue conveys productivity and trust (like Asana, Linear)
- Coral accent adds warmth and energy
- Both themes maintain 4.5:1+ contrast ratios

**Alternatives Rejected**:
- Green-based: Too similar to existing tools (Notion, Evernote)
- Orange primary: Lower contrast, harder to achieve AA compliance
- Monochromatic: Less engaging, doesn't meet "vibrant" requirement

### 3. Background Visual Approach

**Question**: What type of background creates immersion without hurting performance or readability?

**Research**:
- Options: Full image, gradient, abstract pattern, subtle texture
- Performance constraints: Must load fast, < 200KB
- Readability: Must not interfere with text (4.5:1 contrast)

**Decision**: **CSS Gradient with Optional Subtle Pattern**

Primary approach: Multi-stop gradient
```css
background: linear-gradient(135deg,
  hsl(250 100% 97%) 0%,
  hsl(250 80% 95%) 50%,
  hsl(280 60% 96%) 100%
);
```

Optional enhancement: Low-opacity geometric pattern overlay
- SVG pattern: ~5KB inline
- Opacity: 0.03-0.05 (barely visible)

**Rationale**:
- CSS gradients are zero-cost (no network request)
- Creates depth and visual interest
- Easy to adjust for light/dark modes
- Pattern adds premium feel without distraction

**Alternatives Rejected**:
- Full background image: Performance risk, responsive challenges
- Animated gradient: Violates reduced-motion preference principle
- Solid color: Doesn't meet "immersive" requirement

### 4. Button Interaction Design

**Question**: What hover effects feel modern without being distracting?

**Research**:
- Current state: Basic opacity change on hover (`hover:bg-primary/90`)
- Modern patterns: Scale, shadow, color shift, underline animation
- Performance: CSS transforms preferred over layout changes

**Decision**: **Subtle Scale + Shadow Enhancement**

```css
/* Primary button hover */
transform: scale(1.02);
box-shadow: 0 4px 12px -2px rgba(var(--primary), 0.3);
transition: all 200ms ease-out;

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  transform: none;
  transition: opacity 0ms;
}
```

**Rationale**:
- Scale (1.02) is noticeable but subtle—doesn't shift layout
- Shadow adds depth and "liftoff" feel
- 200ms duration feels responsive but smooth
- Respects reduced motion preferences

**Alternatives Rejected**:
- Larger scale (1.05+): Too aggressive, causes layout shifts
- Color flash: Too jarring, accessibility concerns for photosensitive users
- Underline slide: Better for links, not buttons

### 5. Implementation Risk Mitigation

**Question**: How do we ensure existing functionality isn't broken?

**Research**:
- Analyzed current architecture: CSS variables in globals.css, shadcn/ui CVA patterns
- Identified coupling points: CSS variable names, component class names

**Decision**: **Additive-Only Changes**

1. **CSS Variables**: Change values only, never rename
   - Keep `--primary`, `--secondary`, etc. names
   - Only modify the HSL values

2. **Component Classes**: Extend, don't replace
   - Add new transition classes to button variants
   - Keep existing structural classes

3. **New Assets**: Isolated in dedicated location
   - `public/images/` for any new images
   - New CSS classes prefixed with feature identifier if needed

4. **Testing Gates**:
   - After each change: verify app loads
   - After color changes: verify contrast ratios
   - After button changes: click all buttons to verify functionality

**Rationale**:
- Existing code depends on variable names, not values
- shadcn/ui components expect certain class structures
- Additive changes are inherently rollback-safe

## Dependencies Confirmed

| Dependency | Source | License | Bundle Impact |
|------------|--------|---------|---------------|
| Poppins Font | Google Fonts | OFL | ~15KB (woff2, 700 weight only) |
| next/font/google | Next.js built-in | MIT | Already included |
| tailwindcss-animate | npm | MIT | Already installed |

## Technical Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Brand font | Poppins 700 | Modern, pairs with Inter, minimal bundle |
| Color approach | Purple-blue + coral | Vibrant, accessible, distinctive |
| Background | CSS gradient + pattern | Zero network cost, responsive |
| Hover effects | Scale + shadow | Subtle, performant, motion-safe |
| Implementation | Additive only | Zero risk to existing functionality |
