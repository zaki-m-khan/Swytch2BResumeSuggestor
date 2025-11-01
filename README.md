# Resume Annotation Assistant (Local Llama 3.1 8B)

This project ingests a one‑page PDF résumé and a job description, mines skills from the JD, aligns them to résumé sections, and returns non‑destructive annotations (side panel + callouts with arrows) suggesting edits. Inference runs locally with llama.cpp where available; otherwise a deterministic template path is used (suitable for tests/offline).

Highlights
- Privacy-first: no persistence by default; ephemeral processing.
- Non-destructive: suggestions never overwrite the original PDF.
- Accessibility: keyboard navigation and high-contrast overlay.
- Performance: tuned for single-page PDFs with fast heuristics; CPU OK.

Quick Start (local)
- Python: `python -m venv .venv && . .venv/bin/activate` (or `\.\.venv\Scripts\activate` on Windows)
- Install: `pip install -r` (see setup script in the prompt; keep offline after setup)
- Backend: `uvicorn apps.backend.main:app --reload`
- Frontend (optional scaffold): `pnpm --dir apps/frontend dev`

Model (offline)
- Place a GGUF for Meta Llama 3.1 8B Instruct at `models/Meta-Llama-3.1-8B-Instruct.Q4_K_M.gguf` or set `LLAMA_MODEL_PATH`.
- To disable LLM during dev/tests set `LLM_DISABLED=1`.

Environment
- `LLAMA_MODEL_PATH` (optional): path to local GGUF.
- `MAX_UPLOAD_MB` (optional, default 5).

Security & Privacy
- Files are scanned for size/type and processed in-memory.
- No uploads are persisted by default. Add storage only if you opt in.
- Suggestions are framed as “add if true” and never fabricate history.

Testing
- Unit tests (pytest) cover parsers, aligner, annotator and an integration test for `/analyze`.
- E2E (Playwright) test exercises basic UI: uploads, receives annotations, focuses bbox.

License
- Uses permissive OSS (MIT/BSD/Apache-2.0). Ensure you have rights to model artifacts you download.

