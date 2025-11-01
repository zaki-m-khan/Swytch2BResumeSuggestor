export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    const form = await req.formData();
    const backend = process.env.BACKEND_URL || "http://localhost:8000";
    const r = await fetch(`${backend}/analyze`, { method: "POST", body: form });
    const body = await r.text();
    return new Response(body, {
      status: r.status,
      headers: { "content-type": r.headers.get("content-type") || "application/json" }
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || "proxy error" }), { status: 502 });
  }
}

