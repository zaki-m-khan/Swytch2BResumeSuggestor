export async function analyze(params: { resume: File; job_description: string; industry: string; role: string }) {
  const fd = new FormData();
  fd.set("resume", params.resume);
  fd.set("job_description", params.job_description);
  fd.set("industry", params.industry);
  fd.set("role", params.role);
  const r = await fetch("/api/analyze", { method: "POST", body: fd });
  if (!r.ok) {
    let msg = `Analyze failed (${r.status})`;
    try { const t = await r.text(); if (t) msg += `: ${t}`; } catch {}
    throw new Error(msg);
  }
  return await r.json();
}
export async function health() {
  const r = await fetch("/api/health");
  return await r.json();
}
