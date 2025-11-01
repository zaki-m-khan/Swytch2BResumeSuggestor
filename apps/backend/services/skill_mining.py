from typing import Dict, List, Set
import re

INDUSTRY_SEEDS = {
    "software": {"python","react","typescript","api","fastapi","node","docker","aws","sql","testing","java","c++","c/c++","tensorflow","pytorch","ml","machine learning"},
    "healthcare": {"ehr","hipaa","operations","compliance","scheduling","billing"},
    "data": {"python","pandas","numpy","ml","etl","sql","spark"},
}
VERBS = {"built","designed","led","implemented","improved","reduced","increased","optimized"}

def mine_skills(jd_text: str, industry: str) -> Dict[str, Set[str]]:
    text = (jd_text or "").lower()
    words = set(re.findall(r"[a-zA-Z][a-zA-Z\+\/#\-]{1,}", text))
    seeds = INDUSTRY_SEEDS.get(industry.lower(), set())
    phrase_hits = set()
    for phrase in ["machine learning","recommendation systems","data mining","artificial intelligence","c++","c/c++","java","tensorflow","pytorch"]:
        if phrase in text:
            phrase_hits.add(phrase)
    skills = set(w for w in words if w in seeds or w in {"python","react","typescript","docker","aws","api","fastapi","sql","java","c++","tensorflow","pytorch"}) | phrase_hits
    tools = set(x for x in words if x in {"aws","docker","kubernetes","postgres","redis","jira"})
    certs = set(x for x in words if x in {"pmp","aws","azure","gcp"})
    verbs = set(v for v in VERBS if v in text)
    # Fallback: if no explicit skills found, seed with industry defaults to drive generic suggestions
    if not skills and seeds:
        skills = set(list(seeds)[:5])
    return {"skills": skills, "tools": tools, "certs": certs, "verbs": verbs}
