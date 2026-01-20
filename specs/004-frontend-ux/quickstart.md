# Quickstart Guide: Frontend Application & UX

**Feature**: 004-frontend-ux
**Date**: 2026-01-14
**Status**: Complete

This guide helps developers set up and run the frontend application locally.

---

## Prerequisites

- **Node.js**: v20.x or higher (LTS recommended)
- **npm**: v10.x or higher (comes with Node.js)
- **Git**: For version control
- **Backend running**: FastAPI backend must be running on port 8000

### Verify Prerequisites

```bash
# Check Node.js version
node --version
# Expected: v20.x.x or higher

# Check npm version
npm --version
# Expected: 10.x.x or higher

# Verify backend is running
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

---

## 1. Environment Setup

### Clone Repository (if not already done)

```bash
git clone <repository-url>
cd TODO_app
```

### Navigate to Frontend Directory

```bash
cd frontend
```

### Create Environment File

Create `.env.local` from the example:

```bash
cp .env.example .env.local
```

### Configure Environment Variables

Edit `.env.local` with your settings:

```bash
# .env.local

# Better Auth Secret (JWT Signing)
# MUST be identical to backend BETTER_AUTH_SECRET
BETTER_AUTH_SECRET=946ce734e0f4d857fbd8f999c759335349f986f9fb7c9bbacab57b0e102a0887

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Database URL for Better Auth (Neon PostgreSQL)
DATABASE_URL=postgresql://neondb_owner:npg_PCZmgWLYR52j@ep-mute-cell-a1aybmw1-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

> **Important**: The `BETTER_AUTH_SECRET` must match exactly between frontend and backend for JWT validation to work.

---

## 2. Installation

### Install Dependencies

```bash
npm install
```

### Install shadcn/ui Components (if not already installed)

```bash
# Initialize shadcn/ui (if not done)
npx shadcn@latest init

# Install required components
npx shadcn@latest add button card checkbox dialog form input label skeleton alert-dialog dropdown-menu
```

### Install Additional Dependencies

```bash
# Toast notifications
npm install sonner

# Theme management
npm install next-themes

# Form validation
npm install react-hook-form @hookform/resolvers zod
```

---

## 3. Development Server

### Start Backend First

In a separate terminal, ensure the backend is running:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

### Start Frontend Development Server

```bash
# In frontend directory
npm run dev
```

### Access the Application

Open your browser and navigate to:

- **Home**: http://localhost:3000
- **Sign Up**: http://localhost:3000/signup
- **Sign In**: http://localhost:3000/signin
- **Tasks Dashboard**: http://localhost:3000/tasks (requires authentication)

---

## 4. Testing Authentication Flow

### Step 1: Create Account

1. Navigate to http://localhost:3000/signup
2. Enter email: `test@example.com`
3. Enter password: `testpassword123` (min 8 characters)
4. Click "Sign Up"
5. Expected: Redirect to /tasks dashboard

### Step 2: Sign Out

1. Click user menu or "Sign Out" button
2. Expected: Redirect to /signin page

### Step 3: Sign In

1. Navigate to http://localhost:3000/signin
2. Enter email: `test@example.com`
3. Enter password: `testpassword123`
4. Click "Sign In"
5. Expected: Redirect to /tasks dashboard

### Step 4: Verify Protected Routes

1. Sign out
2. Navigate directly to http://localhost:3000/tasks
3. Expected: Redirect to /signin with "Please log in" message

---

## 5. Testing Task CRUD Operations

### Create Task

1. Sign in to the application
2. Click "Add Task" button
3. Enter task title: "My first task"
4. Click "Create" or press Enter
5. Expected: Task appears in list, success toast shown

### Update Task

1. Find a task in the list
2. Click "Edit" button (pencil icon)
3. Modify the title
4. Click "Save" or press Enter
5. Expected: Task title updates, success toast shown

### Toggle Completion

1. Find a task in the list
2. Click the checkbox next to the task
3. Expected:
   - Checkbox fills/unfills
   - Task text gets strikethrough (if completed)
   - Success toast shown

### Delete Task

1. Find a task in the list
2. Click "Delete" button (trash icon)
3. Confirm deletion in dialog
4. Expected: Task removed from list, success toast shown

### View Task Details

1. Click on a task title
2. Expected: Navigate to /tasks/[id] page
3. Verify task details displayed
4. Click "Back to Tasks" to return

---

## 6. Testing Responsive Design

### Mobile View (< 768px)

1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device or set width to 375px
4. Verify:
   - Single-column layout
   - Hamburger menu visible
   - Touch-friendly button sizes
   - Full-width task cards

### Tablet View (768px - 1023px)

1. Set viewport width to 800px
2. Verify:
   - Two-column task grid
   - Collapsible navigation
   - Adjusted spacing

### Desktop View (≥ 1024px)

1. Set viewport width to 1200px
2. Verify:
   - Three-column task grid (or two with sidebar)
   - Full sidebar navigation
   - Optimal reading width

---

## 7. Common Troubleshooting

### CORS Errors

**Symptom**: Network requests fail with CORS error in console.

**Solution**:
1. Ensure backend CORS is configured:
   ```python
   # backend/src/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. Restart backend server

### JWT Token Invalid

**Symptom**: 401 Unauthorized errors on API calls.

**Solution**:
1. Verify `BETTER_AUTH_SECRET` matches in both:
   - `frontend/.env.local`
   - `backend/.env`
2. Clear browser cookies and sign in again
3. Check token expiration (default: 1 hour)

### Module Not Found Errors

**Symptom**: Import errors for shadcn/ui components.

**Solution**:
```bash
# Reinstall the missing component
npx shadcn@latest add <component-name>

# Or reinstall all dependencies
rm -rf node_modules
npm install
```

### Database Connection Errors

**Symptom**: Better Auth fails to initialize.

**Solution**:
1. Verify `DATABASE_URL` in `.env.local`
2. Check Neon database is accessible
3. Verify connection string format includes `?sslmode=require`

### TypeScript Errors

**Symptom**: Type errors in IDE or build.

**Solution**:
```bash
# Clear Next.js cache
rm -rf .next

# Restart TypeScript server in IDE
# VS Code: Ctrl+Shift+P → "TypeScript: Restart TS Server"

# Rebuild
npm run build
```

### Port Already in Use

**Symptom**: `Error: listen EADDRINUSE: address already in use :::3000`

**Solution**:
```bash
# Find and kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :3000
kill -9 <PID>
```

---

## 8. Project Scripts

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Run linter
npm run lint

# Run type check
npm run type-check

# Run tests
npm run test

# Run tests in watch mode
npm run test:watch
```

---

## 9. Directory Structure Overview

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
│   └── layout/             # Layout components
├── lib/                    # Utilities
│   ├── auth.ts             # Better Auth config
│   ├── api-client.ts       # API client
│   └── validations.ts      # Zod schemas
├── types/                  # TypeScript types
├── hooks/                  # Custom hooks
├── public/                 # Static assets
├── tests/                  # Test files
├── .env.local              # Environment variables
└── package.json            # Dependencies
```

---

## 10. Next Steps

After completing the quickstart:

1. **Review the specification**: `specs/004-frontend-ux/spec.md`
2. **Review the plan**: `specs/004-frontend-ux/plan.md`
3. **Check API contracts**: `specs/004-frontend-ux/contracts/`
4. **Run tests**: `npm run test`
5. **Start implementing tasks**: Follow TDD workflow

---

## Support

If you encounter issues not covered here:

1. Check the console for error messages
2. Review the backend logs for API errors
3. Verify environment variables are set correctly
4. Check network tab in DevTools for failed requests

---

**Quickstart Status**: ✅ Complete
**Estimated Setup Time**: < 10 minutes
