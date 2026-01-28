# QA Test Code Generator V2 (Vue.js + FastAPI)

A modern, high-performance web application for generating QA test suites using Gemini 3 Flash. 🚀

## Architecture
- **Frontend**: Vue 3 (Composition API) + Vite + Tailwind CSS
- **Backend**: FastAPI (Pure API) + SSE Streaming
- **Deployment**: Single Container (Multi-stage Docker)

## 🛠 Local Development

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

## 🚢 Production & Deployment
The project uses a **Single Container Strategy**.

1. **Build and Run Locally (Docker):**
```bash
docker build -t qag-vue .
docker run -p 8080:8080 --env-file .env qag-vue
```

2. **Deploy to Cloud Run:**
```bash
./deploy.sh
```

## Folder Structure
- `/backend`: Python service logic and API endpoints.
- `/frontend`: Vue 3 SPA source code.
- `Dockerfile`: Multi-stage build (Node -> Python).
