
# Helio — AI Support Automation Platform

A full-stack AI-powered customer support application built with Python, FastAPI, React, PostgreSQL, Docker and Ollama.

Helio helps support agents manage customer tickets, classify requests using a local language model, and draft responses grounded in company knowledge documents.

## Features

- JWT authentication and password hashing
- User-specific ticket management
- Ticket creation, filtering and status updates
- AI ticket classification and response suggestions
- Retrieval-Augmented Generation (RAG)
- User-specific knowledge base
- Knowledge retrieval using keyword and topic matching
- React dashboard with ticket management and AI tools
- Automated backend tests

## Tech Stack

**Backend:** Python, FastAPI, SQLModel, PostgreSQL, PyJWT

**Frontend:** React, TypeScript, Vite, CSS

**AI:** Ollama, Gemma 3 1B, RAG

**Infrastructure:** Docker, Docker Compose, Git

## Getting Started

Requirements:
- Docker Desktop
- Node.js and npm
- Ollama
- Git

### 1. Clone the repository

git clone https://github.com/Hickey2611/helio-ai-support-platform.git

cd helio-ai-support-platform

### 2. Configure environment variables

Create a `.env` file in the project root:

JWT_SECRET=YOUR_RANDOM_SECRET

Generate a unique cryptographically random secret for local development. Never commit this file.

### 3. Start the backend

docker compose up --build

FastAPI documentation:
http://localhost:8000/docs

### 4. Start Ollama

ollama pull gemma3:1b

Make sure the Ollama server is accessible from the API container.

### 5. Start the frontend

cd frontend

npm install

npm run dev

Open http://localhost:5173

## Testing

Run the backend tests:

docker compose run --rm --no-deps api python -m pytest -q

Last reported local result: 11 passed.

## Architecture

React Dashboard
|
v
FastAPI Backend
|
+-- PostgreSQL (Tickets, Users, Knowledge)
|
+-- Ollama (Gemma 3)
|
+-- AI Classification
+-- RAG Response Generation

## Limitations

- Local-development portfolio application
- AI responses are drafts requiring human review
- Keyword/topic-based retrieval, not vector search
- Not deployed as a public production service
- No email or customer-message delivery integration
- Additional security and deployment testing required

## Screenshots

### Dashboard
![Helio Dashboard](![01-dashboard.png.png](screenshots/01-dashboard.png.png))

### Inbox
![Helio Inbox](![02-inbox.png.png](screenshots/02-inbox.png.png))

### AI-Powered Response
![Helio AI Response](![03-ai-response.png.png](screenshots/03-ai-response.png.png))
## Author

Emyr Hickey

GitHub: https://github.com/Hickey2611

## Project Status

Functional local portfolio MVP. Further production hardening, database migrations and automated security testing are planned.
