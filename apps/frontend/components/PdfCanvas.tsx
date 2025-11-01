"use client";
import React, { useEffect, useRef, useState } from "react";

type Annotation = {
  id: string;
  page: number;
  bbox: [number, number, number, number];
  arrowFrom?: [number, number];
  arrowTo: [number, number];
  suggestion: string;
  rationale: string;
  severity: "high"|"med"|"low";
  tags: string[];
  section: "summary"|"skills"|"experience"|"education"|"projects"|"other";
};

export default function PdfCanvas({
  annotations,
  selectedId,
  onFocusId,
  file,
  pageSize,
  showBoxes = false
}: {
  annotations: Annotation[];
  selectedId: string | null;
  onFocusId: (id: string)=>void;
  file?: File | null;
  pageSize?: [number, number] | null;
  showBoxes?: boolean;
}) {
  const [url, setUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!file) { setUrl(null); return; }
    const u = URL.createObjectURL(file);
    setUrl(u);
    return () => { URL.revokeObjectURL(u); };
  }, [file]);

  const baseW = (pageSize && pageSize[0]) || 600;
  const baseH = (pageSize && pageSize[1]) || 800;
  const scale = 0.9; // render a bit smaller to fit layout
  const viewW = Math.round(baseW * scale);
  const viewH = Math.round(baseH * scale);

  return (
    <div style={{ position: "relative", width: viewW, height: viewH, background: "#f5f5f5", outline: "1px solid #ccc" }} role="figure" aria-label="PDF Page">
      {url ? (
        <iframe title="resume" src={`${url}#toolbar=0&navpanes=0&scrollbar=0&view=FitH`}
                style={{ position:"absolute", inset:0, width:"100%", height:"100%", border:"none", background:"white" }} />
      ) : (
        <div style={{position:"absolute", inset:0, display:"grid", placeItems:"center", color:"#888"}}>Upload a PDF to preview</div>
      )}
      {showBoxes && annotations.map(a => {
        const [x0,y0,x1,y1] = a.bbox;
        const s = {
          left: `${(x0/baseW)*100}%`,
          top: `${(y0/baseH)*100}%`,
          width: `${((x1-x0)/baseW)*100}%`,
          height: `${((y1-y0)/baseH)*100}%`
        } as React.CSSProperties;
        const isSel = selectedId === a.id;
        return (
          <div key={a.id} tabIndex={0}
               onClick={()=>onFocusId(a.id)}
               style={{ position: "absolute", ...s, border: `2px solid ${isSel?"#ff4d4f":"#1677ff"}`, background: isSel?"rgba(255,77,79,0.15)":"rgba(22,119,255,0.12)" }}
               aria-label={`Annotation ${a.section} ${a.tags?.[0]||""}`}>
          </div>
        );
      })}
    </div>
  );
}
