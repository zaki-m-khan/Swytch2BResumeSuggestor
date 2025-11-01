# Resume Annotation Assistant (FastAPI + Next.js + OpenRouter)

This app ingests a one‑page PDF résumé and a job description, mines skills from the JD, aligns them to résumé sections, and returns non‑destructive suggestions in a sidebar. The LLM runs via OpenRouter (remote). PDF overlay boxes are currently disabled for MVP; the viewer shows the PDF and suggestions only.

Highlights
- Privacy-first: no persistence by default; in‑memory processing only.
- Non‑destructive: suggestions never overwrite the original PDF.
- Accessibility: keyboard navigation and high‑contrast UI.
- Simple deploy: Next.js frontend with a small FastAPI backend.

Architecture
- Frontend: Next.js App Router (`apps/frontend`), with proxy routes `/api/analyze` and `/api/health` forwarding to the backend.
- Backend: FastAPI (`apps/backend`) with endpoints `GET /health` and `POST /analyze`.
- LLM: OpenRouter Chat Completions API (model defaults to `meta-llama/llama-3.1-8b-instruct`).

Run locally (Windows PowerShell)
1) Backend (repo root)
   - `cd C:\Users\<you>\btt`
   - `python -m venv .venv`
   - `& .\.venv\Scripts\Activate.ps1`
   - `pip install -U pip`
   - `pip install fastapi uvicorn[standard] pdfplumber rapidfuzz httpx pydantic python-multipart numpy`
   - Create `.env.local` at repo root with:
     - `LLM_API_KEY=sk-or-...` (your OpenRouter key)
     - `LLM_API_BASE=https://openrouter.ai/api/v1`
     - `LLM_MODEL=meta-llama/llama-3.1-8b-instruct`
     - `APP_URL=http://localhost:3000`
     - `APP_NAME=Resume Annotation Assistant`
   - Start backend (from repo root):
     - `uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --reload`
   - Health check: `curl http://localhost:8000/health` → `ready:true, mode:remote` under `llm`.

2) Frontend
   - `cd apps/frontend`
   - `npm install`
   - `npm run dev`
   - Open http://localhost:3000

Usage
- Upload a one‑page, text‑based PDF résumé (not a scan).
- Paste a job description (including a few explicit keywords helps).
- Click Analyze to get LLM‑generated suggestions in the right sidebar.

Environment variables
- Backend (required on the backend host):
  - `LLM_API_KEY` – OpenRouter key
  - `LLM_API_BASE` – default `https://openrouter.ai/api/v1`
  - `LLM_MODEL` – default `meta-llama/llama-3.1-8b-instruct`
  - `APP_URL` – your frontend origin (used for Referer header)
  - `APP_NAME` – display name for OpenRouter header
- Frontend (for hosted deployments):
  - `BACKEND_URL` – public URL of the FastAPI backend; the Next.js proxy calls this.

Deploy notes
- Vercel (frontend): set `BACKEND_URL` only. Do not put `LLM_API_KEY` on Vercel unless you move LLM calls into Next.js.
- Backend host (Render/Fly/Railway/EC2/etc.): set the LLM env vars above and allow CORS from your Vercel URL in `apps/backend/main.py`.

Troubleshooting
- `ModuleNotFoundError: No module named 'apps'`: start uvicorn from the repo root (not `apps/frontend`).
- `/health` shows `mode: local`: ensure `.env.local` exists at repo root or export env vars before starting.
- 400 from OpenRouter: use model id `meta-llama/llama-3.1-8b-instruct` (spelling matters).
- Boxes misaligned: boxes are disabled for MVP; only sidebar suggestions are shown.

Testing
- `pip install pytest pymupdf`
- `pytest -q`

Security & Privacy
- No file persistence by default; in‑memory processing.
- Suggestions use conditional language (“add if true”), never fabricate history.

License
- Permissive OSS (MIT/BSD/Apache-2.0). Keep your API keys private (use `.env.local`, never commit secrets).
