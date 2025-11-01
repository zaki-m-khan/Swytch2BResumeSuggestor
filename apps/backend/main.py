from fastapi import FastAPI, UploadFile, Form, File, Depends, Request
from fastapi.responses import JSONResponse
from typing import List
from apps.backend.schemas import AnnotationResponse, Stats
from apps.backend.services.extract_text import extract_layout
from apps.backend.services.skill_mining import mine_skills
from apps.backend.services.aligner import align
from apps.backend.services.annotator import generate_annotations
from apps.backend.services.llm import critique_and_suggest, llm_ready, llm_info
from apps.backend.security import validate_uploads, rate_limit, MAX_MB
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi import HTTPException

app = FastAPI(title="Resume Annotation Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # Explicit origins to support credentials and ensure ACAO is set
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    # Development-oriented error payload to help diagnose 500s quickly
    try:
        import traceback
        trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    except Exception:
        trace = str(exc)
    print("Unhandled error:", exc)
    return JSONResponse(status_code=500, content={"detail": "internal_error", "error": str(exc), "trace": trace[:2000]})

@app.get("/health")
def health():
    return {"status":"ok", "llm": llm_info()}

@app.get("/")
def root():
    return {"status":"ok","message":"FastAPI is running.","endpoints":["/health","POST /analyze"]}

@app.post("/analyze", response_model=AnnotationResponse)
async def analyze(
    request: Request,
    resume: UploadFile = File(..., description="One-page resume PDF"),
    job_description: str = Form(...),
    industry: str = Form("software"),
    role: str = Form("software_engineer"),
    _: None = Depends(rate_limit),
):
    validate_uploads(resume, job_description)
    if not llm_ready():
        info = llm_info()
        raise HTTPException(status_code=503, detail=f"LLM not loaded: {info.get('error')}. Set LLAMA_MODEL_PATH to your GGUF.")
    pdf_bytes = await resume.read()
    # Simple debug print to surface in server logs
    print(f"/analyze called: industry={industry} role={role} file={getattr(resume,'filename',None)} len(pdf)={len(pdf_bytes)}")
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(pdf_bytes) > MAX_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large; limit is {MAX_MB} MB")
    if not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF. Please upload a real PDF.")
    try:
        layout = extract_layout(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")
    jd = mine_skills(job_description, industry)
    al = align(jd, layout["sections"])
    ann = generate_annotations(al, layout)
    llm = critique_and_suggest(jd, layout)
    stats = Stats(
        matched=len(al["matches"]),
        gaps=len(al["gaps"]),
        partial=len(al["partial"]),
        jd_skills=len(jd.get("skills",[])),
    )
    return AnnotationResponse(
        annotations=ann,
        jd_summary=llm.get("jd_summary",""),
        resume_summary=llm.get("resume_summary",""),
        stats=stats,
        page_size=layout.get("page_size"),
    )
