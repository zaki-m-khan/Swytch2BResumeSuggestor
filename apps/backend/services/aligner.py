from typing import Dict, Any, List, Tuple
from rapidfuzz import fuzz

def align(jd: Dict[str, set], resume_sections: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map JD skills to résumé sections. Compute matches/gaps with simple fuzzy match.
    """
    full_text = " ".join(v.get("text","") for v in resume_sections.values()).lower()
    out = {"matches": [], "gaps": [], "partial": []}
    for skill in sorted(jd.get("skills", set())):
        score = 0
        best_section = "skills"
        for sec_name, sec in resume_sections.items():
            stext = (sec.get("text","") or "").lower()
            local = max(
                fuzz.partial_ratio(skill, stext),
                fuzz.partial_ratio(skill, full_text),
            )
            if local > score:
                score = local
                best_section = sec_name
        entry = {"skill": skill, "section": best_section, "score": score}
        if score >= 85:
            out["matches"].append(entry)
        elif score >= 50:
            out["partial"].append(entry)
        else:
            out["gaps"].append(entry)
    return out
