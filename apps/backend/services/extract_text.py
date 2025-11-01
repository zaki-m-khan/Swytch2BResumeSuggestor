from typing import Dict, Any, List, Tuple
import io
import pdfplumber

SECTIONS = ["contact","summary","skills","experience","education","projects"]

def _default_layout(page_width: float, page_height: float) -> Dict[str, Any]:
    bands = {}
    band_h = page_height / 6.0
    for i, name in enumerate(SECTIONS):
        y0 = i * band_h
        y1 = y0 + band_h
        bands[name] = {"page": 0, "bbox": (0.0, y0, page_width, y1), "text": ""}
    return bands

def extract_layout(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Extract simple one-page layout with coarse section bands and text.
    Heuristic: divide page into 6 horizontal bands in expected résumé order.
    Populate section text from page text (best-effort).
    """
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        if len(pdf.pages) == 0:
            raise ValueError("Empty PDF")
        page = pdf.pages[0]
        w, h = page.width, page.height
        layout = _default_layout(w, h)
        text = (page.extract_text() or "").strip()
        # word-level positions for anchoring annotations
        words_raw = page.extract_words(x_tolerance=2, y_tolerance=2) or []
        words = [
            {
                "text": w.get("text",""),
                "bbox": (float(w.get("x0",0.0)), float(w.get("top",0.0)), float(w.get("x1",0.0)), float(w.get("bottom",0.0)))
            }
            for w in words_raw
            if w.get("text")
        ]
        lower = text.lower()
        # Heuristic splits by section keywords if present
        buckets: Dict[str, List[str]] = {k: [] for k in SECTIONS}
        current = "summary"
        for line in text.splitlines():
            l = line.strip()
            ll = l.lower()
            if "skill" in ll:
                current = "skills"
            elif "experience" in ll or "work history" in ll:
                current = "experience"
            elif "education" in ll:
                current = "education"
            elif "project" in ll:
                current = "projects"
            elif any(x in ll for x in ["address","email","phone","linkedin","github"]) or current=="summary" and len(buckets["contact"])<3:
                current = "contact"
            buckets[current].append(l)
        for k in SECTIONS:
            layout[k]["text"] = "\n".join(buckets.get(k, []))
        # Ensure some summaries
        if not layout["summary"]["text"] and text:
            layout["summary"]["text"] = text.split("\n")[0][:300]
        return {"page_size": (w, h), "sections": layout, "full_text": text, "words": words}
