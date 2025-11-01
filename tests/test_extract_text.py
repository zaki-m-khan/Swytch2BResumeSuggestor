import io
import fitz  # PyMuPDF
from apps.backend.services.extract_text import extract_layout

def _pdf_with_text(lines):
    doc = fitz.open()
    page = doc.new_page(width=600, height=800)
    y = 50
    for ln in lines:
        page.insert_text((50, y), ln, fontsize=12)
        y += 20
    b = doc.tobytes()
    doc.close()
    return b

def test_extract_layout_basic():
    pdf = _pdf_with_text([
        "John Doe | email@example.com | 555-555-5555",
        "Summary", "Software engineer with Python and React.",
        "Skills", "Python, FastAPI, React, SQL",
        "Experience", "Built APIs and UIs",
        "Education", "BS CS",
        "Projects", "Portfolio site"
    ])
    layout = extract_layout(pdf)
    assert "sections" in layout
    assert layout["sections"]["skills"]["text"].lower().find("python") >= 0

