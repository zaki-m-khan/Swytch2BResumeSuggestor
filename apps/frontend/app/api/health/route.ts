export const runtime = "nodejs";

export async function GET() {
  const backend = process.env.BACKEND_URL || "http://localhost:8000";
  const r = await fetch(`${backend}/health`);
  const body = await r.text();
  return new Response(body, {
    status: r.status,
    headers: { "content-type": r.headers.get("content-type") || "application/json" }
  });
}

