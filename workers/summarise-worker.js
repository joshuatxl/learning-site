/* Cloudflare Worker: on-demand article summariser.
 *
 * POST { "url": "<article url>", "title": "<optional>" }
 *   -> { "summary": "<~300 words>" }
 *
 * Fetches the article server-side, strips it to text, and asks Gemini for a
 * ~300-word summary. Called only when the visitor clicks "Summarise this",
 * so Gemini is never invoked during the daily build.
 *
 * Secrets / vars (set with `wrangler secret put` or in the dashboard):
 *   GEMINI_API_KEY   (required)
 *   GEMINI_MODEL     (optional, default "gemini-2.0-flash")
 *   ALLOW_ORIGIN     (optional, default "*"; set to your Pages origin to lock down)
 */

const TAG_RE = /<(script|style)[\s\S]*?<\/\1>|<[^>]+>/gi;

function textFromHtml(html) {
  const body = html.replace(/[\s\S]*?<body[^>]*>/i, "").replace(/<\/body>[\s\S]*/i, "");
  return (body || html)
    .replace(TAG_RE, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&#39;|&rsquo;|&lsquo;/g, "'")
    .replace(/&quot;|&ldquo;|&rdquo;/g, '"')
    .replace(/\s+/g, " ")
    .trim();
}

function json(obj, status, cors) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...cors },
  });
}

export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return json({ error: "POST only" }, 405, cors);
    if (!env.GEMINI_API_KEY) return json({ error: "GEMINI_API_KEY not set" }, 500, cors);

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid JSON body" }, 400, cors);
    }
    const url = (body && body.url ? String(body.url) : "").trim();
    const title = (body && body.title ? String(body.title) : "").trim();
    if (!/^https?:\/\//i.test(url)) return json({ error: "missing or bad url" }, 400, cors);

    let text = "";
    try {
      const res = await fetch(url, {
        headers: { "User-Agent": "Mozilla/5.0 (compatible; BriefingBot/1.0)" },
        cf: { cacheTtl: 3600, cacheEverything: true },
      });
      if (res.ok) text = textFromHtml(await res.text()).slice(0, 14000);
    } catch {
      /* fall through — summarise from the title alone */
    }

    const prompt =
      "Summarise the following article in about 300 words. Be specific and " +
      "factual, focus on what is new or notable, and do not add a preamble or " +
      "sign-off.\n\nTitle: " + (title || "(unknown)") + "\n\n" + (text || title);

    const model = env.GEMINI_MODEL || "gemini-2.0-flash";
    const api =
      "https://generativelanguage.googleapis.com/v1beta/models/" +
      model + ":generateContent?key=" + env.GEMINI_API_KEY;

    let g;
    try {
      g = await fetch(api, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: { temperature: 0.3, maxOutputTokens: 700 },
        }),
      });
    } catch (e) {
      return json({ error: "gemini request failed: " + e.message }, 502, cors);
    }
    if (!g.ok) return json({ error: "gemini HTTP " + g.status, detail: await g.text() }, 502, cors);

    const data = await g.json();
    const summary =
      (data.candidates &&
        data.candidates[0] &&
        data.candidates[0].content &&
        data.candidates[0].content.parts &&
        data.candidates[0].content.parts[0] &&
        data.candidates[0].content.parts[0].text) || "";

    return json({ summary: summary.trim() }, 200, cors);
  },
};
