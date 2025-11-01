from fastapi.testclient import TestClient
from apps.backend.main import app
import fitz
import io

def _pdf():
    doc = fitz.open()
    p = doc.new_page(width=600, height=800)
    p.insert_text((50,50), "Summary")
    p.insert_text((50,70), "Python developer experienced with APIs and React")
    p.insert_text((50,120), "Skills")
    p.insert_text((50,140), "Python, FastAPI, SQL")
    b = doc.tobytes()
    doc.close()
    return b

def test_analyze_endpoint_ok():
    c = TestClient(app)
    files = {"resume": ("resume.pdf", _pdf(), "application/pdf")}
    data = {"job_description": "We need Python, React, FastAPI", "industry":"software", "role":"software_engineer"}
    r = c.post("/analyze", data=data, files=files)
    assert r.status_code == 200
    js = r.json()
    assert "annotations" in js and isinstance(js["annotations"], list)
    assert "jd_summary" in js and "resume_summary" in js

