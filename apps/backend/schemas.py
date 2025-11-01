from typing import List, Literal, Tuple, Optional, Dict, Any
from pydantic import BaseModel, Field

BBox = Tuple[float, float, float, float]
Point = Tuple[float, float]
SectionName = Literal["summary","skills","experience","education","projects","other"]
Severity = Literal["high","med","low"]

class Annotation(BaseModel):
    id: str
    page: int = 0
    bbox: BBox
    arrowFrom: Optional[Point] = None
    arrowTo: Point
    suggestion: str
    rationale: str
    severity: Severity = "med"
    tags: List[str] = []
    section: SectionName = "other"

class Stats(BaseModel):
    matched: int = 0
    gaps: int = 0
    partial: int = 0
    jd_skills: int = 0

class AnnotationResponse(BaseModel):
    annotations: List[Annotation]
    jd_summary: str
    resume_summary: str
    stats: Stats
    page_size: Optional[Tuple[float, float]] = None
