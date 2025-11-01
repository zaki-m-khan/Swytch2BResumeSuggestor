from apps.backend.services.annotator import generate_annotations

def test_generate_annotations_creates_gaps():
    align_out = {"matches": [], "partial": [], "gaps": [{"skill":"react","section":"skills","score":0}]}
    layout = {"page_size": (600,800), "sections": {"skills": {"bbox": (0,100,600,200)}}}
    anns = generate_annotations(align_out, layout)
    assert len(anns) == 1
    a = anns[0]
    assert a.section == "skills"
    assert "react" in a.suggestion.lower()

