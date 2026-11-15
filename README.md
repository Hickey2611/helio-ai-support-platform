# AI Support Automation Platform — backend starter

A portfolio project built with Python, FastAPI, PostgreSQL, Docker and SQLModel.

**Current scope:** ticket CRUD basics (create, list, get, update status), validation, interactive API docs and tests. **AI responses, authentication, RAG and deployment are not implemented yet.** Do not present this as a completed AI product in your CV.

## Requirements
- Docker Desktop with Docker Compose, or Python 3.12+

## Run with Docker (PostgreSQL)
```bash
docker compose up --build
```
Open **http://localhost:8000/docs** to try the API.

To stop: `Ctrl+C`, then `docker compose down`.

## Run locally without Docker (SQLite)
On Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open **http://127.0.0.1:8000/docs**.

## Test
```bash
python -m pytest -q
```

## Try POST /tickets in Swagger
```json
{
  "customer_email": "customer@example.com",
  "subject": "Where is my order?",
  "message": "My delivery has not arrived."
}
```

## Next milestones
1. Authentication and organization-level isolation; database migrations.
2. Knowledge-base documents and semantic retrieval (RAG).
3. LLM-drafted responses with citations, confidence checks and human review.
4. Background jobs, logging, security hardening, tests, CI and deployment.

> Local development only. The API has no authentication yet. Don't expose it publicly or upload real customer data.
