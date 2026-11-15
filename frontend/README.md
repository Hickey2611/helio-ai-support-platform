# Helio — React frontend for AI Support Automation Platform

A local-development, responsive dashboard that connects to the existing FastAPI project.

## What it does

- Sign in and register via `/auth/token` and `/auth/register`
- View tickets assigned to the logged-in account, create tickets, change status
- Run the backend's `/ai-analyze` and `/rag-analyze` endpoints and inspect suggested replies
- View, add, and delete user-owned knowledge articles
- Dashboard cards based on real API responses, not sample data

## Requirements

1. Working FastAPI backend with `/auth`, `/tickets`, `/knowledge`, and `/rag-analyze` endpoints, launched with `docker compose up --build` on port 8000.
2. Node.js 20.19+ or 22.12+ and npm on Windows.
3. Ollama + `gemma3:1b` running for AI features.

## Run (IntelliJ IDEA terminal / Windows PowerShell)

Place `frontend` directory inside your existing `ai-support-platform` project; do **not** replace the backend `app` directory.

```powershell
cd C:\Users\emirh\Documents\Projects\ai-support-platform\frontend
npm install
npm run dev
```

Open http://localhost:5173. If Vite prints http://127.0.0.1:5173, use that URL.

The Vite proxy forwards requests under `/api` to `http://127.0.0.1:8000` and strips `/api`. **Do not add CORS middleware just for this local setup.**

## Local-only security notes

- Access tokens are held in React state, not localStorage. Refreshing the page signs you out.
- For development only. Frontend routes are **not** a security boundary: backend JWT and user ownership checks are essential.
- Do not expose the Vite development server to the internet or use real customer data.
- Do not commit `.env`, API secrets, or database volumes.
- No messages are automatically sent to customers. AI responses are drafts requiring human review.
- The app expects API validation and status enums from the backend. If changing a status fails, check `TicketStatus` in `app/models.py`.

## Production later

Run `npm run build` for static files, configure a reverse proxy for `/api`, use HTTPS and secure server-managed sessions, then add proper deployment testing.
