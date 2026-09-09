# Summariser worker

Backs the **"Summarise this"** button on the front page. A static GitHub Pages
site can't call Gemini directly, so this tiny Cloudflare Worker does it: it
fetches the article, strips it to text, and asks Gemini for ~300 words.

Gemini is only ever called when a visitor clicks the button.

## Deploy (free tier)

```bash
cd workers
npm i -g wrangler           # or: npx wrangler ...
wrangler login
wrangler secret put GEMINI_API_KEY   # paste your key
wrangler deploy
```

`wrangler deploy` prints a URL like
`https://briefing-summarise.<subdomain>.workers.dev`.

## Wire it to the site

Put that URL in `mkdocs.yml`:

```yaml
extra:
  summarise_url: "https://briefing-summarise.<subdomain>.workers.dev"
```

Rebuild / redeploy the site. Done — the button now calls the worker, and each
result is cached in the visitor's browser (`localStorage`) so re-opening is free.

## Options (set in `wrangler.toml` `[vars]` or the dashboard)

| var | default | purpose |
|-----|---------|---------|
| `GEMINI_API_KEY` | – | **required**, set as a secret |
| `GEMINI_MODEL` | `gemini-2.0-flash` | any current Gemini model id |
| `ALLOW_ORIGIN` | `*` | set to your Pages origin to lock down CORS |

## Prefer Python?

`ingest/summarise.py` already contains the same ~300-word prompt against the
`google-genai` SDK. Wrap `summarise(text, title)` in a FastAPI route and host it
anywhere; point `summarise_url` at that instead.
