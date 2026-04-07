# AI-Powered Hospital Receptionist

A production-ready full-stack hospital receptionist assistant built with React + Vite + Tailwind, FastAPI, LangGraph, Supabase, and webhook integration to relay.app.

## Features

- Natural language chat interface with step-by-step patient data collection
- Name, age, and symptom capture with validation
- Rule-based and AI-enhanced ward classification
- Supabase persistence with UUID records and timestamp
- Secure webhook trigger to `https://relay.app` after completion
- Docker-ready backend and frontend

## Project Structure

- `frontend/` — React + Vite UI
- `backend/` — FastAPI backend, LangGraph workflow, Supabase and webhook services
- `docker-compose.yml` — optional local deployment
- `.gitignore` — ignored files

## Setup

### 1. Configure environment variables

Create backend `.env` from `.env.example` and populate:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
RELAY_APP_URL=https://relay.app
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_KEY=change-with-secure-key
```

Create frontend `.env` from `.env.example` if you need to override backend URL:

```env
VITE_BACKEND_URL=http://localhost:8000
```

### 2. Install backend dependencies

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd ../frontend
npm install
```

### 4. Run Supabase database setup

Create a table named `patients` with columns:

- `id` (uuid, primary key)
- `patient_name` (text)
- `patient_age` (integer)
- `patient_query` (text)
- `ward` (text)
- `timestamp` (text)
- `created_at` (timestamp with time zone)

### 5. Start the backend

```bash
cd ../backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start the frontend

```bash
cd ../frontend
npm run dev
```

Then open `http://localhost:5173`.

## API Endpoints

- `POST /chat` — handles conversational turns; accepts `user_message` and optional `session_state`
- `POST /webhook` — sends patient registration payload to relay.app

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

## Notes

- The backend uses environment variables and secure API key validation.
- The LangGraph workflow modularizes the conversation flow into input processing, classification, clarification, completion, and webhook trigger.
- The frontend UI includes message bubbles, typing state, summary card, and responsive layout.
