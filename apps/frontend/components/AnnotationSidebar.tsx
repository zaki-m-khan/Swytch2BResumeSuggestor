"use client";
type Annotation = {
  id: string;
  suggestion: string;
  rationale: string;
  section: string;
};

export default function AnnotationSidebar({ annotations, onSelect }: { annotations: Annotation[], onSelect: (id: string)=>void }) {
  return (
    <aside style={{ width: 360, maxHeight: 800, overflow: "auto", borderLeft: "1px solid #eee", paddingLeft: 8 }}>
      <h3>Suggestions</h3>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {annotations.map(a=>(
          <li key={a.id} style={{ marginBottom: 8 }}>
            <button onClick={()=>onSelect(a.id)} style={{ display: "block", width: "100%" }}>
              <strong>[{a.section}]</strong> {a.suggestion}
            </button>
            <div style={{ fontSize: 12, color: "#666" }}>{a.rationale}</div>
          </li>
        ))}
      </ul>
    </aside>
  );
}

