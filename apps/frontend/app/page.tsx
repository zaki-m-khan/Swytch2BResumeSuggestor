"use client";
import { useState } from "react";
import { analyze } from "../lib/api";
import PdfCanvas from "../components/PdfCanvas";
import AnnotationSidebar from "../components/AnnotationSidebar";

export default function Home() {
  const [resume, setResume] = useState<File | null>(null);
  const [jd, setJd] = useState("");
  const [industry, setIndustry] = useState("software");
  const [role, setRole] = useState("software_engineer");
  const [data, setData] = useState<any | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const onSubmit = async (e: any) => {
    e.preventDefault();
    setError(null);
    if (!resume) { setError("Please choose a PDF resume."); return; }
    if (!jd.trim()) { setError("Please paste a job description."); return; }
    try {
      setLoading(true);
      setInfo(null);
      const resp = await analyze({ resume, job_description: jd, industry, role });
      setData(resp);
      if (!resp?.annotations?.length) {
        setInfo("No specific suggestions detected. Try adding explicit keywords to the JD (e.g., Python, React).");
      }
    } catch (err: any) {
      console.error(err);
      setError(err?.message || "Analyze failed. Check backend is running on :8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ display: "flex", gap: 16, padding: 16 }}>
      <form onSubmit={onSubmit} style={{ display: "grid", gap: 8, width: 360 }}>
        <input type="file" accept="application/pdf" onChange={(e)=>setResume(e.target.files?.[0]||null)} />
        {resume && <div style={{fontSize:12,color:'#999'}}>Selected: {resume.name}</div>}
        <select value={industry} onChange={(e)=>setIndustry(e.target.value)}>
          <option value="software">Software</option>
          <option value="healthcare">Healthcare</option>
          <option value="data">Data</option>
        </select>
        <select value={role} onChange={(e)=>setRole(e.target.value)}>
          <option value="software_engineer">Software Engineer</option>
          <option value="healthcare_admin">Healthcare Admin</option>
          <option value="data_analyst">Data Analyst</option>
        </select>
        <textarea placeholder="Paste job description..." rows={8} value={jd} onChange={(e)=>setJd(e.target.value)} />
        <button type="submit" disabled={!resume || !jd.trim() || loading}>{loading?"Analyzing...":"Analyze"}</button>
        {error && <div role="alert" style={{ color: '#ff4d4f', fontWeight:600 }}>{error}</div>}
        {info && !error && <div role="status" style={{ color: '#1677ff' }}>{info}</div>}
      </form>
      <div style={{ display: "flex", gap: 16, flex: 1 }}>
        <PdfCanvas annotations={data?.annotations||[]} selectedId={selected} onFocusId={setSelected} file={resume} pageSize={data?.page_size} showBoxes={false} />
        <AnnotationSidebar annotations={data?.annotations||[]} onSelect={setSelected} />
      </div>
    </main>
  );
}
