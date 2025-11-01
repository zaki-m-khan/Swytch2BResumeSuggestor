import uuid
from typing import Dict, Any, List
from apps.backend.schemas import Annotation
from apps.backend.services.llm import phrase_for_skill

ALLOWED_SECTIONS = {"summary","skills","experience","education","projects","other"}

def _normalize_section(name: str) -> str:
    return name if name in ALLOWED_SECTIONS else "other"

def _arrow_for(bbox, page_w):
    x0,y0,x1,y1 = bbox
    cx = (x0+x1)/2
    cy = (y0+y1)/2
    return (page_w + 20.0, cy), (cx, cy)

def _find_word_bbox(layout: Dict[str,Any], term: str):
    term_l = term.lower()
    words = layout.get("words", [])
    # Try exact/substring match in a single word
    for w in words:
        if term_l in (w["text"] or "").lower():
            return w["bbox"]
    # Try first token of multi-word skill
    parts = [p for p in term_l.replace("/"," ").split() if p]
    if parts:
        head = parts[0]
        for w in words:
            if head in (w["text"] or "").lower():
                return w["bbox"]
    return None

def generate_annotations(align_out: Dict[str, Any], layout: Dict[str, Any]) -> List[Annotation]:
    ann: List[Annotation] = []
    page_w, page_h = layout["page_size"]
    sections = layout["sections"]
    section_offsets: Dict[str,int] = {k:0 for k in sections.keys()}
    # For gaps: suggest adding truthful content
    for g in align_out["gaps"]:
        # Try to anchor to a matching word on page; else to section with slight offset
        word_bbox = _find_word_bbox(layout, g["skill"]) or sections.get(g["section"], sections["skills"]) ["bbox"]
        # Apply vertical jitter to avoid perfect overlap
        sec_name = g.get("section","skills")
        sec = sections.get(sec_name, sections["skills"])
        x0,y0,x1,y1 = sec["bbox"]
        offset = section_offsets.get(sec_name,0)
        section_offsets[sec_name] = offset + 1
        if word_bbox:
            anchor = word_bbox
        else:
            band_h = (y1-y0)
            anchor = (x0, y0 + min(offset,4)*band_h/5, x0+band_h/10, y0 + min(offset+1,5)*band_h/5)
        af, at = _arrow_for(anchor, page_w)
        ann.append(Annotation(
            id=str(uuid.uuid4()),
            page=0,
            bbox=anchor,
            arrowFrom=af,
            arrowTo=at,
            suggestion=phrase_for_skill(g["skill"], _normalize_section(g.get("section","other")), layout.get("full_text","")),
            rationale="Bridge the gap between JD requirements and your résumé; add truthful evidence.",
            severity="high",
            tags=["gap", g["skill"]],
            section=_normalize_section(g.get("section","other")),
        ))
    # For partial: refine phrasing
    for p in align_out["partial"]:
        word_bbox = _find_word_bbox(layout, p["skill"]) or sections.get(p["section"], sections["skills"]) ["bbox"]
        sec_name = p.get("section","skills")
        sec = sections.get(sec_name, sections["skills"])
        x0,y0,x1,y1 = sec["bbox"]
        offset = section_offsets.get(sec_name,0)
        section_offsets[sec_name] = offset + 1
        if not word_bbox:
            band_h = (y1-y0)
            word_bbox = (x0, y0 + min(offset,4)*band_h/5, x0+band_h/10, y0 + min(offset+1,5)*band_h/5)
        af, at = _arrow_for(word_bbox, page_w)
        ann.append(Annotation(
            id=str(uuid.uuid4()),
            page=0,
            bbox=word_bbox,
            arrowFrom=af,
            arrowTo=at,
            suggestion=phrase_for_skill(p["skill"], _normalize_section(p.get("section","other")), layout.get("full_text","")),
            rationale="Detected a partial match; being explicit improves ATS and reviewer alignment.",
            severity="med",
            tags=["refine", p["skill"]],
            section=_normalize_section(p.get("section","other")),
        ))
    # For matches: encourage quantification/impact
    for m in align_out.get("matches", [])[:5]:
        word_bbox = _find_word_bbox(layout, m["skill"]) or sections.get(m["section"], sections["skills"]) ["bbox"]
        af, at = _arrow_for(word_bbox, page_w)
        ann.append(Annotation(
            id=str(uuid.uuid4()),
            page=0,
            bbox=word_bbox,
            arrowFrom=af,
            arrowTo=at,
            suggestion=f"If true, quantify impact for '{m['skill']}' (numbers, scale, latency, revenue).",
            rationale="Even when present, explicit metrics improve clarity and ATS signals.",
            severity="low",
            tags=["quantify", m["skill"]],
            section=_normalize_section(m.get("section","other")),
        ))
    # If still empty, add one generic annotation pointing to summary
    if not ann:
        sec = sections.get("summary", list(sections.values())[0])
        af, at = _arrow_for(sec["bbox"], page_w)
        ann.append(Annotation(
            id=str(uuid.uuid4()),
            page=0,
            bbox=sec["bbox"],
            arrowFrom=af,
            arrowTo=at,
            suggestion="Tailor your summary and skills to the JD’s top competencies (add if true).",
            rationale="No explicit JD keywords were detected; align phrasing to highlight relevant experience.",
            severity="low",
            tags=["general"],
            section="summary",
        ))
    return ann
