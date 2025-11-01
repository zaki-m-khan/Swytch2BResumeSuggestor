from apps.backend.services.aligner import align

def test_align_maps_gaps_and_matches():
    jd = {"skills": {"python","react"}}
    resume_sections = {
        "skills": {"text":"Python, FastAPI, SQL", "bbox": (0,0,600,100)},
        "experience": {"text":"Built APIs", "bbox": (0,100,600,200)}
    }
    out = align(jd, resume_sections)
    skills = {e["skill"] for e in out["matches"]} | {e["skill"] for e in out["partial"]} | {e["skill"] for e in out["gaps"]}
    assert {"python","react"}.issubset(skills)
    assert any(e["skill"]=="react" for e in out["gaps"])

