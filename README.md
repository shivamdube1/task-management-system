# TaskFlow — Role-Based Task Management System

A full-stack web application implementing a role-based access control (RBAC) task management system with separate Admin and User dashboards.

## 🏗️ Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18 + TypeScript + Vite | Fast SPA bundling with type safety; Vite over Next.js since this is a dashboard-heavy app that doesn't require SSR |
| **State Management** | Zustand | Lightweight, zero-boilerplate global state |
| **UI Components** | Vanilla CSS + Lucide React | Premium dark theme with glassmorphism; Lucide for consistent icons |
| **HTTP Client** | Axios | Request/response interceptors for JWT auto-attach and 401 refresh |
| **Backend** | FastAPI (Python 3.12) | Async-capable, auto-generated OpenAPI docs, built-in validation |
| **ORM** | SQLAlchemy 2.0 | Industry-standard Python ORM with relationship mapping |
| **Migrations** | Alembic | Versioned database schema migrations |
| **Database** | PostgreSQL 16 | Production-grade relational database |
| **Auth** | JWT (python-jose) + bcrypt (passlib) | Stateless authentication with secure password hashing |
| **Testing** | pytest + FastAPI TestClient | Integration tests with in-memory SQLite |
| **Containerization** | Docker + Docker Compose | One-command full-stack deployment |

## 📋 Features

### Authentication & Authorization
- User registration with role selection (Admin / User)
- JWT-based authentication with access + refresh tokens
- Automatic token refresh on 401 responses
- Role-based route protection (frontend + backend)
- Secure password hashing with bcrypt

### Admin Dashboard
- **Create tasks** — Title, description, priority, status, due date, assignee
- **View all tasks** — Paginated grid with filter by status and priority
- **Edit tasks** — Modal form with pre-populated fields
- **Delete tasks** — With confirmation dialog
- **User management** — List users for task assignment
- **Dashboard stats** — Total, pending, completed, and overdue task counts

### User Dashboard
- **View assigned tasks only** — Server-filtered by `assigned_to`
- **Update task status** — Forward-only transitions: `pending → in_progress → completed`
- **Overdue highlighting** — Red left border on overdue tasks
- **Status badges** — Color-coded priority and status indicators

### UI/UX
- Premium dark theme with glassmorphism effects
- Responsive layout (desktop sidebar + mobile hamburger)
- Smooth animations and micro-interactions
- Loading spinners on all async operations
- Toast notifications for success/error feedback
- Inline form validation with descriptive error messages

## 🚀 Setup Instructions

### Prerequisites
- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 16 (or use Docker)

### Option 1 — Docker Compose (Recommended)

```bash
# Clone and start everything
docker-compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2 — Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL connection string

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start dev server
npm run dev
```

### Running Tests

```bash
cd backend
pytest -v
```

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://tms_user:tms_pass@localhost:5432/tms_db` |
| `SECRET_KEY` | JWT signing secret (change in production!) | `change-this-...` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `FRONTEND_ORIGIN` | CORS allowed origin | `http://localhost:5173` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

## 📡 API Documentation

Interactive Swagger UI is available at `http://localhost:8000/docs` when the backend is running.

### Auth Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/auth/register` | Public | Create a new user account |
| `POST` | `/api/auth/login` | Public | Authenticate and receive JWT tokens |
| `POST` | `/api/auth/refresh` | Refresh token | Issue new access token |
| `POST` | `/api/auth/logout` | Bearer | Stateless logout |
| `GET` | `/api/auth/me` | Bearer | Get current user profile |

### Task Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `POST` | `/api/tasks` | Bearer | Admin | Create a task |
| `GET` | `/api/tasks` | Bearer | Admin | List all tasks (filterable) |
| `PUT` | `/api/tasks/{id}` | Bearer | Admin | Update a task |
| `DELETE` | `/api/tasks/{id}` | Bearer | Admin | Delete a task |
| `GET` | `/api/tasks/my` | Bearer | Any | List current user's assigned tasks |
| `PATCH` | `/api/tasks/{id}/status` | Bearer | Any | Update task status (forward-only) |

### User Endpoints

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| `GET` | `/api/users` | Bearer | Admin | List all users (for assignee dropdown) |

### Example Request — Create Task

```json
POST /api/tasks
Authorization: Bearer <access_token>

{
  "title": "Design dashboard mockups",
  "description": "Create UI mockups for the admin and user dashboards",
  "priority": "high",
  "due_at": "2025-07-01T15:30:00Z",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Example Response

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "title": "Design dashboard mockups",
  "description": "Create UI mockups for the admin and user dashboards",
  "priority": "high",
  "status": "pending",
  "due_at": "2025-07-01T15:30:00Z",
  "assigned_to": "550e8400-e29b-41d4-a716-446655440000",
  "created_by": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "created_at": "2025-06-23T10:00:00Z",
  "updated_at": "2025-06-23T10:00:00Z",
  "assignee": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Jane User",
    "email": "jane@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2025-06-20T08:00:00Z"
  },
  "creator": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "name": "Admin User",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2025-06-19T08:00:00Z"
  }
}
```

## 🗄️ Database Schema

### Users Table

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | Primary Key, auto-generated |
| `name` | VARCHAR(100) | NOT NULL |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| `hashed_password` | VARCHAR(255) | NOT NULL |
| `role` | ENUM('admin','user') | NOT NULL, default 'user' |
| `is_active` | BOOLEAN | default true |
| `created_at` | TIMESTAMPTZ | auto-set |

### Tasks Table

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | Primary Key, auto-generated |
| `title` | VARCHAR(100) | NOT NULL |
| `description` | TEXT | nullable |
| `priority` | ENUM('low','medium','high') | NOT NULL, default 'medium' |
| `status` | ENUM('pending','in_progress','completed') | NOT NULL, default 'pending' |
| `due_at` | TIMESTAMPTZ | NOT NULL |
| `assigned_to` | UUID | FK → users.id, ON DELETE SET NULL |
| `created_by` | UUID | FK → users.id |
| `created_at` | TIMESTAMPTZ | auto-set |
| `updated_at` | TIMESTAMPTZ | auto-update |

**Relationship:** `users` 1 → N `tasks` (via `assigned_to`)

## 📝 Assumptions Made

1. **Token storage**: Tokens are stored in `localStorage`. This is simpler than httpOnly cookies but has a known XSS trade-off. For production, consider using httpOnly cookies with CSRF protection.
2. **No email verification**: Registration does not require email verification for simplicity.
3. **UTC datetimes**: All timestamps are stored and transmitted in UTC (ISO 8601). The frontend converts to local timezone for display.
4. **Status transitions are one-directional by design**: `pending → in_progress → completed`. Once completed, a task cannot revert. This prevents ambiguity in task tracking.
5. **Admins can set any status directly** when creating or editing tasks.
6. **Refresh tokens are stateless**: No server-side token blacklist. Logout is client-side only.
7. **Role assignment at registration**: Users choose their role (admin/user) during sign-up. In production, admin roles would be assigned by a superadmin.

## ⚠️ Known Limitations

1. **No refresh token rotation** — the same refresh token is valid until it expires
2. **No per-IP rate limiting** — should be added via middleware or reverse proxy
3. **Polling instead of WebSocket** — tasks refresh every 30 seconds via polling, not real-time push
4. **No email notifications** — users must check the dashboard for new assignments
5. **No pagination** on task lists — all tasks are loaded at once
6. **SQLite used in tests** — production uses PostgreSQL, so some edge cases (e.g., enum types) may differ

## 🧪 Test Coverage

| Test | Type | Assertion |
|------|------|-----------|
| Register success | Integration | 201 + user object |
| Duplicate email | Integration | 409 Conflict |
| Invalid email format | Integration | 422 Validation |
| Login success | Integration | 200 + both tokens |
| Wrong password | Integration | 401 Unauthorized |
| Nonexistent user login | Integration | 401 Unauthorized |
| Access /me without token | Integration | 401 Unauthorized |
| Access /me with valid token | Integration | 200 + user |
| Admin creates task | Integration | 201 + task |
| User cannot create task | Integration | 403 Forbidden |
| Admin lists all tasks | Integration | 200 + array |
| Admin deletes task | Integration | 204 |
| User sees only own tasks | Integration | Filtered response |
| Status forward transition | Integration | 200 OK |
| Status backward rejected | Integration | 400 Bad Request |
| Completed task is terminal | Integration | 400 Bad Request |

## 📁 Project Structure

```
task-management-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py              # Auth dependencies
│   │   │   └── routes/
│   │   │       ├── auth.py          # Auth endpoints
│   │   │       ├── tasks.py         # Task CRUD
│   │   │       └── users.py         # User list
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings
│   │   │   ├── security.py          # JWT + bcrypt
│   │   │   └── exceptions.py        # Global handlers
│   │   ├── db/
│   │   │   ├── base.py              # SQLAlchemy Base
│   │   │   └── session.py           # DB session
│   │   ├── models/
│   │   │   ├── user.py              # User ORM
│   │   │   └── task.py              # Task ORM
│   │   ├── schemas/
│   │   │   ├── auth.py              # Auth schemas
│   │   │   ├── task.py              # Task schemas
│   │   │   └── user.py              # User schemas
│   │   └── main.py                  # FastAPI app
│   ├── alembic/                     # Migrations
│   ├── tests/                       # Integration tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/axios.ts             # Axios + interceptors
│   │   ├── components/              # Reusable components
│   │   ├── hooks/                   # Custom hooks
│   │   ├── pages/                   # Page components
│   │   ├── store/authStore.ts       # Zustand auth state
│   │   ├── types/index.ts           # TypeScript interfaces
│   │   └── utils/dateFormat.ts      # Date helpers
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
