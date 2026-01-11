# Tailwind CSS Reference Guide for Next.js 16

## Core Concepts

### Utility-First Approach
Tailwind CSS is a utility-first CSS framework packed with classes that can be composed to build any design, directly in your markup. Instead of pre-defined component classes, you apply small, single-purpose classes to build your design.

### Responsive Design
Tailwind uses a mobile-first approach with responsive prefixes:
- `sm:` - 640px and above
- `md:` - 768px and above
- `lg:` - 1024px and above
- `xl:` - 1280px and above
- `2xl:` - 1536px and above

### Dark Mode
Configure dark mode in `tailwind.config.ts`:
```js
module.exports = {
  darkMode: 'class', // or 'media'
  // ...
}
```

Then use the `dark:` prefix: `dark:bg-gray-800`

## Commonly Used Utilities

### Layout
- `container` - Centered container with max-width based on breakpoints
- `flex`, `inline-flex` - Display utilities
- `grid` - CSS Grid layout
- `hidden` - `display: none`
- `block`, `inline-block` - Display utilities

### Spacing
- `p-{n}` - Padding (0, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64)
- `m-{n}` - Margin (0, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 56, 64)
- `space-x-{n}` - Space between children horizontally
- `space-y-{n}` - Space between children vertically
- `gap-{n}` - Gap for flexbox and grid layouts

### Typography
- `text-{size}` - Font sizes (xs, sm, base, lg, xl, 2xl, 3xl, 4xl, 5xl, 6xl, 7xl, 8xl, 9xl)
- `font-{weight}` - Font weights (thin, extralight, light, normal, medium, semibold, bold, extrabold, black)
- `leading-{size}` - Line heights (none, tight, snug, normal, relaxed, loose)
- `tracking-{size}` - Letter spacing (tighter, tight, normal, wide, wider, widest)

### Colors
- `bg-{color}-{shade}` - Background colors
- `text-{color}-{shade}` - Text colors
- `border-{color}-{shade}` - Border colors
- `divide-{color}-{shade}` - Divide colors

Common color shades: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900

### Flexbox & Grid
- `flex-row`, `flex-col` - Flex direction
- `items-{alignment}` - Align items (start, center, end, baseline, stretch)
- `justify-{alignment}` - Justify content (start, center, end, between, around, evenly)
- `flex-{grow|shrink|wrap}` - Flex properties

### Sizing
- `w-{size}` - Width (full, screen, min, max, fit, 1/2, 1/3, 2/3, 1/4, 2/4, 3/4, etc.)
- `h-{size}` - Height (full, screen, min, max, fit, 1, 2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32, etc.)

### Borders
- `border` - Border width (default: 1px)
- `border-{size}` - Border width (0, 2, 4, 8)
- `rounded-{size}` - Border radius (none, sm, md, lg, xl, 2xl, 3xl, full)
- `border-{side}` - Border on specific sides (t, r, b, l)

### Effects
- `shadow-{size}` - Box shadows (sm, md, lg, xl, 2xl, inner, none)
- `opacity-{value}` - Opacity (0, 5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 100)
- `ring-{size}` - Focus rings (ring-2, ring-4, etc.)

### Transitions & Animation
- `transition` - Default transition
- `transition-{property}` - Specific transitions (color, bg, all, etc.)
- `duration-{ms}` - Transition duration (75, 100, 150, 200, 300, 500, 700, 1000)
- `ease-{type}` - Easing functions (linear, in, out, in-out)

## Common Component Patterns

### Card
```html
<div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
  <!-- Card content -->
</div>
```

### Button
```html
<!-- Primary button -->
<button class="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors">
  Button Text
</button>

<!-- Secondary button -->
<button class="border border-gray-300 hover:border-gray-400 text-gray-700 dark:text-gray-300 font-medium py-2 px-4 rounded-md transition-colors">
  Button Text
</button>
```

### Form Input
```html
<div class="mb-4">
  <label class="block text-gray-700 dark:text-gray-300 text-sm font-medium mb-2" for="input">
    Label
  </label>
  <input class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" id="input" type="text">
</div>
```

## Responsive Breakpoints

| Breakpoint | Class Prefix | Minimum Width | CSS Media Query |
|------------|--------------|---------------|-----------------|
| Small | `sm:` | 640px | `@media (min-width: 640px)` |
| Medium | `md:` | 768px | `@media (min-width: 768px)` |
| Large | `lg:` | 1024px | `@media (min-width: 1024px)` |
| Extra Large | `xl:` | 1280px | `@media (min-width: 1280px)` |
| 2x Extra Large | `2xl:` | 1536px | `@media (min-width: 1536px)` |

## State Variants

- `hover:` - Applied on hover
- `focus:` - Applied when focused
- `active:` - Applied when active
- `disabled:` - Applied when disabled
- `group-hover:` - Applied when parent group is hovered
- `focus-within:` - Applied when element or child is focused

## Dark Mode Variants

- `dark:` - Applied in dark mode (when `class="dark"` is on the html element)

## Customizing Tailwind

### Adding Custom Colors
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'primary': '#3b82f6',
        'secondary': '#64748b',
      }
    }
  }
}
```

### Adding Custom Spacing
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    }
  }
}
```

## Performance Optimization

### Purge Unused Classes
Configure the content paths in `tailwind.config.js`:
```js
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  // ...
}
```

### Safelisting Classes
For dynamically generated classes:
```js
// tailwind.config.js
module.exports = {
  safelist: [
    'bg-red-500',
    'text-blue-600',
    {
      pattern: /bg-(red|green|blue)-(100|200|300)/,
    },
  ],
  // ...
}
```

## Accessibility Considerations

- Use sufficient color contrast (4.5:1 for normal text, 3:1 for large text)
- Implement proper focus states: `focus:outline-none focus:ring-2 focus:ring-blue-500`
- Use semantic HTML elements
- Provide ARIA attributes when necessary
- Test with screen readers
- Ensure keyboard navigation works properly