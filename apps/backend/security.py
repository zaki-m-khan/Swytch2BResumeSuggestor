import os
from fastapi import HTTPException, UploadFile, Request

MAX_MB = int(os.getenv("MAX_UPLOAD_MB","5"))

def validate_uploads(resume: UploadFile, job_text: str):
    if resume is None or resume.filename is None or not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="resume.pdf is required and must be a PDF.")
    if len(job_text or "") < 20:
        raise HTTPException(status_code=400, detail="Job description too short.")

async def rate_limit(request: Request):
    # Simple per-process counter; placeholder non-persistent limiter
    return

