# AI-Powered Hospital Receptionist

A production-ready full-stack hospital receptionist assistant built with React + Vite + Tailwind, FastAPI, LangGraph, Supabase, and webhook integration to relay.app.

## 🚀 Features

- 💬 **Natural language chat interface** with step-by-step patient data collection
- 👤 **Smart validation** for name, age, and symptoms
- 🏥 **AI-enhanced ward classification** with 6 specialized wards:
  - Emergency Ward (life-threatening conditions)
  - Mental Health Ward (psychological care)
  - Cardiology Ward (heart conditions)
  - Orthopedics Ward (bone/joint issues)
  - Pediatrics Ward (children's care)
  - General Ward (other conditions)
- 🗄️ **Supabase persistence** with UUID records and timestamps
- 🔗 **Secure webhook integration** to relay.app after completion
- 🐳 **Docker-ready** for easy deployment
- 🔒 **API authentication** and CORS protection

## 🏗️ Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.10 + Uvicorn
- **AI Workflow**: LangGraph for conversational state management
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Docker + docker-compose
- **Webhook**: HTTP POST to relay.app

## 📁 Project Structure

```
├── frontend/          # React + Vite UI
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Environment config
│   │   ├── schemas.py        # Pydantic models
│   │   ├── services/         # Business logic
│   │   └── routers/          # API endpoints
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile
├── docker-compose.yml # Local deployment
└── README.md
```

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
python3.11 -m venv .venv
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

## 🚀 Deployment

### Docker (Recommended)

```bash
# Build and run with docker-compose
docker-compose up --build
```

### Cloud Platforms

- **Railway**: Connect GitHub repo, auto-detects Docker
- **Render**: Web services from Docker  
- **Vercel + Railway**: Frontend on Vercel, backend on Railway

Set these environment variables in your hosting platform:

```env
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_KEY=your-prod-service-role-key
RELAY_APP_URL=https://relay.app
API_KEY=secure-random-api-key
```

## 📡 API Documentation

### POST `/chat`

Chat endpoint for patient registration conversation.

**Headers:**
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request:**
```json
{
  "user_message": "John Doe",
  "session_state": {
    "patient_name": null,
    "patient_age": null,
    "patient_query": null,
    "ward": null,
    "completed": false
  }
}
```

**Response:**
```json
{
  "assistant_message": "Thanks John. What is your age?",
  "session_state": {
    "patient_name": "John Doe",
    "patient_age": null,
    "completed": false
  },
  "patient_summary": null
}
```

### GET `/`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Hospital receptionist backend is running."
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

Built with ❤️ for healthcare innovation
