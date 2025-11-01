from apps.backend.services.skill_mining import mine_skills

def test_mine_skills_detects_core():
    jd = "Seeking Software Engineer with Python, APIs, React and cloud experience."
    res = mine_skills(jd, "software")
    assert "python" in res["skills"]
    assert "react" in res["skills"]

