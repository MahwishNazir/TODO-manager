# Todo App Frontend

A production-ready Next.js 16 frontend for the multi-user Todo application with JWT authentication and responsive design.

## Features

- User authentication (signup, signin, logout)
- Full task CRUD operations (Create, Read, Update, Delete)
- Task completion toggle
- Responsive mobile-first design
- Dark/Light theme support
- Toast notifications for user feedback

## Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript 5+
- **UI Components**: shadcn/ui + Radix UI
- **Styling**: Tailwind CSS 4
- **Authentication**: Better Auth with JWT
- **Form Handling**: React Hook Form + Zod
- **Notifications**: Sonner

## Prerequisites

- Node.js 20.x or higher
- npm 10.x or higher
- Backend API running on port 8000

## Installation

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Configure environment variables**:

   ```bash
   cp .env.example .env.local
   ```

   Edit `.env.local` with your settings:

   ```bash
   # Better Auth Secret (must match backend)
   BETTER_AUTH_SECRET=your-secret-key

   # Backend API URL
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Database URL for Better Auth
   DATABASE_URL=your-neon-database-url
   ```

3. **Start development server**:

   ```bash
   npm run dev
   ```

4. **Open in browser**:

   Navigate to [http://localhost:3000](http://localhost:3000)

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Create production build |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/             # Auth pages (signin, signup)
│   ├── tasks/              # Task pages (dashboard, detail)
│   ├── api/                # API routes (Better Auth)
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page
├── components/             # React components
│   ├── ui/                 # shadcn/ui components
│   ├── tasks/              # Task-specific components
│   ├── auth/               # Auth components
│   ├── layout/             # Layout components
│   └── providers/          # Context providers
├── lib/                    # Utilities
│   ├── auth.ts             # Better Auth config
│   ├── auth-client.ts      # Auth client utilities
│   ├── api-client.ts       # API client
│   ├── validations.ts      # Zod schemas
│   └── constants.ts        # App constants
├── types/                  # TypeScript types
├── hooks/                  # Custom React hooks
└── public/                 # Static assets
```

## Authentication Flow

1. **Signup**: Create account at `/signup` with email and password
2. **Signin**: Login at `/signin` with credentials
3. **Protected Routes**: Access `/tasks` requires authentication
4. **Session**: JWT tokens stored in HttpOnly cookies
5. **Logout**: Clear session and redirect to signin

## API Integration

The frontend connects to the FastAPI backend at `NEXT_PUBLIC_API_URL`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/{user_id}/tasks` | GET | List all tasks |
| `/api/{user_id}/tasks` | POST | Create new task |
| `/api/{user_id}/tasks/{id}` | GET | Get task details |
| `/api/{user_id}/tasks/{id}` | PUT | Update task |
| `/api/{user_id}/tasks/{id}` | DELETE | Delete task |
| `/api/{user_id}/tasks/{id}/complete` | PATCH | Toggle completion |

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | Single column, hamburger menu |
| Tablet | 768px - 1023px | Two column grid |
| Desktop | >= 1024px | Three column grid, full sidebar |

## Theme Support

Toggle between light and dark themes using the theme button in the header. Theme preference is persisted in localStorage.

## Troubleshooting

### CORS Errors

Ensure backend CORS is configured to allow `http://localhost:3000`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### JWT Token Invalid

1. Verify `BETTER_AUTH_SECRET` matches in frontend and backend
2. Clear browser cookies and sign in again
3. Check token expiration (default: 1 hour)

### Module Not Found

```bash
rm -rf node_modules
npm install
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (must match backend) |
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL |
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

ISC
