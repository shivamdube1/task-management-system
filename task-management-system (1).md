# 🗂️ Task Management System — Full Stack Engineering Assignment

> **Assignment Type:** Full Stack Take-Home / Hiring Assessment
> **Estimated Time:** 4–6 hours
> **Submission:** GitHub Repository + Deployed Link (optional)

---

## 📌 Overview

Build a **Role-Based Task Management System** where:

- **Admins** can create and assign tasks to users with a due date & time, and track task progress.
- **Users** can view their assigned tasks on a personal dashboard and update task status.
- Both roles authenticate via **JWT-based authentication**.

This assignment evaluates your ability to design and implement a production-grade full-stack application — clean architecture, security, real-world UX, and code quality all matter.

---

## 🧱 Tech Stack (Fixed)

| Layer | Required |
|---|---|
| **Frontend** | React.js (Vite) **or** Next.js 14+ (App Router) |
| **Backend** | Python — **FastAPI** |
| **Database** | PostgreSQL (preferred) or SQLite (local dev only) |
| **ORM** | SQLAlchemy + Alembic |
| **Auth** | JWT + bcrypt password hashing |
| **Validation** | Pydantic v2 (built into FastAPI) |

---

## 🔐 Feature 1 — Authentication (JWT + Role-Based)

Implement a complete authentication system with two roles: `admin` and `user`.

- Users register with a name, email, password, and role.
- On login, the server returns a **JWT access token** (expires in 15 minutes) and a **refresh token** (expires in 7 days).
- All passwords must be **hashed with bcrypt** before being stored — plaintext passwords are not acceptable.
- The JWT payload must carry the user's ID, email, and role.
- Every protected route must verify the token. Requests without a valid token return `401 Unauthorized`.
- Routes restricted to admins must reject user-role tokens with `403 Forbidden`.
- On the frontend, after login the user is redirected to their role-specific dashboard. A route guard prevents unauthenticated users from accessing any dashboard page.

### Endpoints

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
POST   /api/auth/logout
GET    /api/auth/me
```

---

## 🛠️ Feature 2 — Admin Dashboard

Admins have full control over task creation and management.

- Admin can create a task by filling in a **title** (max 100 characters), an optional **description** (max 500 characters), selecting the **user to assign it to** from a dropdown, picking a **due date and time** using a calendar and time picker UI, and setting a **priority** of Low, Medium, or High.
- Admin can view all tasks across all users, with the ability to filter by status, assigned user, and priority.
- Admin can edit or delete any task.
- When a task is created or updated, the change must be visible on the assigned user's dashboard — polling every 30 seconds is acceptable.

### Endpoints

```
POST   /api/tasks
GET    /api/tasks
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
GET    /api/users
```

---

## 👤 Feature 3 — User Dashboard

Users have a read-and-update view of only their own tasks.

- A user must only ever see tasks assigned to them — this filtering must happen server-side, never on the client.
- Each task displays its title, description, priority, due date and time, and current status.
- A user can move a task forward through the status progression: `pending` → `in_progress` → `completed`. This is one-directional — a completed task cannot be reverted.
- Tasks that are past their due date and still not completed must be visually highlighted (e.g., a red border or badge).
- Users cannot create, delete, or reassign tasks.

### Endpoints

```
GET    /api/tasks/my
PATCH  /api/tasks/{task_id}/status
```

---

## 🗓️ Feature 4 — Date & Time Selection (Admin UI)

The task creation and edit form must include a proper **calendar date picker** and a **time picker** — not a plain HTML date input. Past dates must be disabled so admins cannot schedule tasks in the past. The final selected value must be sent to the backend as a single ISO 8601 timezone-aware datetime string, and displayed on task cards in a readable format such as `Mon, 23 Jun 2025 at 3:30 PM`.

---

## 🧪 Technical Requirements

### Backend

- [ ] JWT verification applied to all protected routes via FastAPI `Depends()`
- [ ] A `require_admin` dependency that wraps the auth check and enforces role
- [ ] All request and response bodies validated through Pydantic v2 — no manual validation
- [ ] A global exception handler returning a consistent `{ "detail": "message" }` shape
- [ ] Database schema managed through Alembic migrations
- [ ] CORS configured to allow only the frontend origin
- [ ] At least **5 tests** using `pytest` + `httpx.AsyncClient` covering auth and task routes

### Frontend

- [ ] Axios instance with a request interceptor that attaches the `Authorization: Bearer` header
- [ ] Response interceptor that automatically refreshes the token on `401` and retries the request
- [ ] Client-side form validation with clear inline error messages
- [ ] Error details returned by FastAPI displayed to the user — not silently swallowed
- [ ] Loading and error states on every async operation
- [ ] Fully responsive layout — works on mobile and desktop

### General

- [ ] `.env.example` files committed for both frontend and backend with placeholder values
- [ ] No secrets or credentials committed to the repository
- [ ] Clean, consistent folder structure throughout

---

## 📝 README Requirements

Your submitted `README.md` must include:

1. **Project Overview** — what the app does and which frontend framework you chose and why
2. **Tech Stack** — every major library used on both sides
3. **Setup Instructions** — step-by-step commands to run backend and frontend locally
4. **Environment Variables** — every variable documented with a description
5. **API Documentation** — all endpoints with method, path, auth requirement, request body, and example response
6. **Database Schema** — description of the `users` and `tasks` tables and their relationship
7. **Assumptions Made** — any decisions where the spec was ambiguous
8. **Known Limitations** — honest about what you'd improve with more time

---

## 🎯 Evaluation Criteria

| Criteria | Weight |
|---|---|
| Authentication & Security (JWT, bcrypt, role guards) | 25% |
| FastAPI backend design (Pydantic, dependency injection, error handling) | 20% |
| Frontend UX (dashboard usability, date/time picker, responsiveness) | 20% |
| Code quality (clean structure, type hints, no dead code) | 15% |
| Database design (models, migrations, relationships) | 10% |
| Tests | 10% |

---

## 🚀 Bonus Points *(not required, but impressive)*

- WebSocket or SSE for real-time task updates
- Email notification when a task is assigned
- Task activity log tracking every status change with a timestamp
- Pagination and sorting on task list endpoints
- Docker Compose to run the full stack with a single command
- Deployed live link

---

## 📤 Submission

1. Push your code to a **public GitHub repository** named `task-management-system` or `tms-[yourname]`.
2. Submit the repository link along with a short Loom walkthrough (3–5 min) if possible.
3. Include any notes on what you'd improve given more time.

> ⏰ **Deadline:** As communicated separately. Late submissions may not be reviewed.

---

## ❓ Questions?

Reach out via email before the deadline. Do not ask for feature clarifications after submitting — document your assumptions instead.

---

*Good luck. We look forward to reviewing your work.*
