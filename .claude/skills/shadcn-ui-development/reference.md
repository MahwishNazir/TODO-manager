# shadcn/ui Reference for Todo App Development

## Installation Commands

### Initialize shadcn/ui
```bash
npx shadcn@latest init
```
- Creates `components.json` configuration
- Sets up base styles and aliases
- Configures import paths

### Add Components
```bash
# Add specific components
npx shadcn@latest add @shadcn/button
npx shadcn@latest add @shadcn/input
npx shadcn@latest add @shadcn/label
npx shadcn@latest add @shadcn/card
npx shadcn@latest add @shadcn/form
npx shadcn@latest add @shadcn/checkbox
npx shadcn@latest add @shadcn/dialog
npx shadcn@latest add @shadcn/sheet
npx shadcn@latest add @shadcn/sonner
```

### Add Multiple Components at Once
```bash
npx shadcn@latest add @shadcn/button @shadcn/input @shadcn/label @shadcn/card @shadcn/form @shadcn/checkbox @shadcn/dialog @shadcn/sheet @shadcn/sonner @shadcn/skeleton @shadcn/spinner @shadcn/sidebar @shadcn/alert @shadcn/avatar @shadcn/calendar @shadcn/tooltip
```

## Key Components for Todo App

### Core Components
- **Card**: Container for task items and forms
- **Input**: Text input fields for task titles
- **Button**: Action buttons for creating, editing, deleting tasks
- **Checkbox**: Completion status toggle
- **Dialog**: Confirmation dialogs for destructive actions
- **Form**: Structured forms with validation
- **Label**: Accessible labels for form elements
- **Sonner**: Toast notifications for user feedback

### Advanced Components
- **Sheet**: Mobile-friendly side panels for task details
- **Textarea**: Multi-line input for task descriptions
- **Separator**: Visual separation between tasks
- **Skeleton**: Loading placeholders for better UX
- **Spinner**: Visual feedback during async operations
- **Sidebar**: Navigation menu for app sections
- **Alert/AlertDialog**: Notifications and confirmation dialogs
- **Avatar**: User profile pictures and initials
- **Calendar/DatePicker**: Date selection for due dates
- **Tooltip**: Hover information for UI elements
- **Theme Toggle**: Dark/light mode switching functionality

## Using shadcn MCP Tools

### Component Discovery and Usage
- **Search components**: Use `mcp__shadcn__search_items_in_registries` to find components by name
- **Get examples**: Use `mcp__shadcn__get_item_examples_from_registries` to see real implementation examples
- **Get installation commands**: Use `mcp__shadcn__get_add_command_for_items` for exact installation syntax
- **View component details**: Use `mcp__shadcn__view_items_in_registries` for component information
- **Check project registries**: Use `mcp__shadcn__get_project_registries` to see configured registries

### Common Search Queries
- Search for specific components: `skeleton`, `sidebar`, `alert`, `avatar`, `calendar`, `tooltip`, `spinner`
- Search for functionality: `loading`, `date`, `navigation`, `user`, `theme`
- Get examples with patterns like: `component-name demo` or `component-name example`

## Configuration (components.json)

The default configuration created by `npx shadcn@latest init`:

```json
{
  "style": "new-york",
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "typescript": true
}
```

## Import Aliases

- `@/components/ui/` - shadcn/ui components
- `@/components/` - Custom components
- `@/lib/utils` - Utility functions (like `cn` for class merging)
- `@/hooks/` - Custom React hooks

## Styling Approach

### Tailwind CSS Integration
- All components use Tailwind utility classes
- CSS variables for theming (defined in `:root`)
- Responsive design out of the box
- Dark mode support

### Utility Classes
- `cn()` function for conditional class merging
- Consistent spacing and sizing system
- Accessible color contrast ratios

## Form Handling Patterns

### React Hook Form + Zod
```tsx
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
})
```

### TanStack Form + Zod
```tsx
import { useForm } from "@tanstack/react-form"
import * as z from "zod"

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().optional(),
})
```

## Accessibility Features

### ARIA Attributes
- Proper labeling with `aria-labelledby` and `aria-describedby`
- Keyboard navigation support
- Screen reader compatibility
- Focus management

### Semantic HTML
- Proper heading hierarchy
- Correct use of form elements
- Landmark regions

## TypeScript Integration

### Component Props
- Strongly typed component props
- Form schema validation
- Event handler typing
- Ref typing where needed

### Utility Types
- Form data types from Zod schemas
- Component variant types
- Event types for better intellisense