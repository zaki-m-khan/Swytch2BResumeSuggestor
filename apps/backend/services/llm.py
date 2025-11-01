import os
from typing import Dict, Any
import json
import httpx

_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "models/Meta-Llama-3.1-8B-Instruct.Q4_K_M.gguf")

# Mutable globals — will be refreshed from env as needed
_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
_API_BASE = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1")
_API_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
_APP_URL = os.getenv("APP_URL", "http://localhost:3000")
_APP_NAME = os.getenv("APP_NAME", "Resume Annotation Assistant")
_MODE = "remote" if _API_KEY else "local"

_LLM = None
_LOAD_ERR: str | None = None

def _refresh_from_env():
    global _API_KEY, _API_BASE, _API_MODEL, _APP_URL, _APP_NAME, _MODE, _LLM, _LOAD_ERR
    _load_env_from_files()
    # Pull latest env; allows switching to remote without restarting the process
    _API_KEY = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    _API_BASE = os.getenv("LLM_API_BASE", _API_BASE)
    _API_MODEL = os.getenv("LLM_MODEL", _API_MODEL)
    _APP_URL = os.getenv("APP_URL", _APP_URL)
    _APP_NAME = os.getenv("APP_NAME", _APP_NAME)
    _MODE = "remote" if _API_KEY else "local"
    _API_MODEL = _canonical_model(_API_MODEL)
    if _MODE == "local" and _LLM is None:
        try:
            if os.path.exists(_MODEL_PATH):
                from llama_cpp import Llama
                _LLM = Llama(model_path=_MODEL_PATH, n_ctx=4096, n_threads=int(os.getenv("LLAMA_THREADS","4")))
                print(f"[LLM] Loaded llama.cpp model: {_MODEL_PATH}")
                _LOAD_ERR = None
            else:
                _LOAD_ERR = f"Model file not found at {_MODEL_PATH}. Set LLAMA_MODEL_PATH to your GGUF or configure LLM_API_KEY for remote."
        except Exception as e:
            _LOAD_ERR = str(e)
            _LLM = None

def _load_env_from_files():
    """Best-effort loader for .env files in dev. Only sets keys that are missing.
    Files checked (first found wins per key): .env.local, .env
    Search paths: CWD, repo root (../../.. from this file), and this file's dir.
    """
    candidates = [
        os.getcwd(),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")),
        os.path.dirname(__file__),
    ]
    names = [".env.local", ".env"]
    for base in candidates:
        for name in names:
            path = os.path.join(base, name)
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and (k not in os.environ or not os.environ.get(k)):
                            os.environ[k] = v
            except Exception:
                pass

def _canonical_model(model: str) -> str:
    if not model:
        return model
    m = model.strip()
    aliases = {
        "meta-llama/Meta-Llama-3.1-8B-Instruct": "meta-llama/llama-3.1-8b-instruct",
        "Meta-Llama-3.1-8B-Instruct": "meta-llama/llama-3.1-8b-instruct",
        "llama-3.1-8b-instruct": "meta-llama/llama-3.1-8b-instruct",
    }
    return aliases.get(m, m)

def llm_ready() -> bool:
    _refresh_from_env()
    if _MODE == "remote":
        return bool(_API_KEY) and bool(_API_MODEL)
    return _LLM is not None

def llm_info() -> Dict[str, Any]:
    _refresh_from_env()
    return {
        "ready": llm_ready(),
        "mode": _MODE,
        "model": _API_MODEL if _MODE == "remote" else _MODEL_PATH,
        "base_url": _API_BASE if _MODE == "remote" else None,
        "error": _LOAD_ERR,
    }

SYSTEM = (
    "You are a resume coach. Suggest concise, natural, actionable edits. "
    "Never fabricate; always use conditional language (e.g., 'add if true', 'consider highlighting'). "
    "Tie suggestions to the job description and to real experiences only."
)

def _template(jd, layout) -> Dict[str, Any]:
    skills = sorted(list(jd.get("skills", set())))
    lines = [
        (
            "- You could add concise evidence for: "
            + ", ".join(skills[:8])
            + " (if true)."
        ) if skills else ""
    ]
    return {
        "jd_summary": f"Core competencies: {', '.join(skills[:10])}" if skills else "No specific skills detected.",
        "resume_summary": (layout.get("full_text","") or "")[:200],
        "section_suggestions": {
            "summary": "Align your summary to the JD’s top competencies. " + (lines[0] if skills else ""),
            "skills": "Surface the exact terms used in the JD and group them meaningfully (e.g., ML, backend, cloud).",
            "experience": "Use specific outcomes tied to JD skills (if true), e.g., 'reduced latency 25% using X'.",
            "education": "Surface relevant coursework/certs if applicable.",
            "projects": "Include 1–2 projects demonstrating JD-aligned tools (real only).",
        }
    }

def critique_and_suggest(jd: Dict[str, Any], layout: Dict[str, Any]) -> Dict[str, Any]:
    _refresh_from_env()
    msgs = [
        {"role":"system","content": SYSTEM},
        {"role":"user","content": f"JD text skills: {sorted(list(jd.get('skills',[])))}\nResume summary: {(layout.get('full_text','') or '')[:800]}\nReturn JSON with fields jd_summary, resume_summary and brief per-section tips."}
    ]
    if _MODE == "remote":
        headers = {
            "Authorization": f"Bearer {_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": _APP_URL,
            "X-Title": _APP_NAME,
        }
        try:
            resp = httpx.post(
                f"{_API_BASE}/chat/completions",
                headers=headers,
                json={
                    "model": _API_MODEL,
                    "messages": msgs,
                    "temperature": 0.2,
                },
                timeout=45,
            )
            if resp.status_code >= 400:
                try:
                    err = resp.json()
                except Exception:
                    err = {"text": resp.text}
                raise RuntimeError(f"Remote LLM error {resp.status_code}: {err}")
            content = resp.json()["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            raise RuntimeError(f"Remote LLM network error: {e}")
    else:
        if _LLM is None:
            raise RuntimeError(_LOAD_ERR or "LLM not loaded")
        out = _LLM.create_chat_completion(messages=msgs, temperature=0.2)
        content = out["choices"][0]["message"]["content"]
    # Best-effort: fall back to template on parse errors
    try:
        import json
        data = json.loads(content)
        return data
    except Exception:
        return _template(jd, layout)

def phrase_for_skill(skill: str, section: str, jd_text: str) -> str:
    """Return a single natural suggestion sentence for a skill.
    Uses LLM if available; otherwise a clean template."""
    _refresh_from_env()
    prompt = (
        "Job description excerpt:\n" + jd_text[:600] +
        f"\nSkill: {skill}\nSection: {section}\n"
        "Write one concise sentence advising how to reflect this skill in the specified section. "
        "Be natural and conditional (add if true). Do not invent facts."
    )
    if _MODE == "remote":
        headers = {
            "Authorization": f"Bearer {_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": _APP_URL,
            "X-Title": _APP_NAME,
        }
        resp = httpx.post(
            f"{_API_BASE}/chat/completions",
            headers=headers,
            json={
                "model": _API_MODEL,
                "messages": [
                    {"role":"system","content": SYSTEM},
                    {"role":"user","content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 120,
            },
            timeout=45,
        )
        if resp.status_code >= 400:
            try:
                err = resp.json()
            except Exception:
                err = {"text": resp.text}
            raise RuntimeError(f"Remote LLM error {resp.status_code}: {err}")
        return resp.json()["choices"][0]["message"]["content"].strip()
    else:
        if _LLM is None:
            raise RuntimeError(_LOAD_ERR or "LLM not loaded")
        out = _LLM.create_chat_completion(messages=[
            {"role":"system","content": SYSTEM},
            {"role":"user","content": prompt}
        ], temperature=0.3)
        return out["choices"][0]["message"]["content"].strip()
