export type Annotation = {
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
export type AnnotationResponse = {
  annotations: Annotation[];
  jd_summary: string;
  resume_summary: string;
  stats: { matched: number; gaps: number; partial: number; jd_skills: number };
}

