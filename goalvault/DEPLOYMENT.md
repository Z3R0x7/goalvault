# GoalVault — Hosting & API Key Security

## Where to host (recommended)

| Platform | Best for | Free tier | Database |
|----------|----------|-----------|----------|
| **Railway** | Fastest hackathon deploy | Yes | Add PostgreSQL plugin |
| **Render** | Stable free web service | Yes | Render PostgreSQL |
| **Fly.io** | Global edge | Limited free | SQLite or Postgres |

### Recommended: Railway

1. Push `goalvault/` to GitHub (do not commit `.env`).
2. Create project at [railway.app](https://railway.app) → Deploy from GitHub.
3. Add **PostgreSQL** service → copy `DATABASE_URL`.
4. Set variables in Railway dashboard (see below).
5. Set start command: `gunicorn run:app --bind 0.0.0.0:$PORT`
6. Run once: `railway run python seed_data.py`

Your live URL will look like: `https://goalvault-production.up.railway.app`

### Alternative: Render

1. New **Web Service** → connect repo, root directory `goalvault`.
2. Build: `pip install -r requirements.txt`
3. Start: `gunicorn run:app`
4. Add **PostgreSQL** and link `DATABASE_URL`.
5. Shell → `python seed_data.py`

---

## API keys you need

| Variable | Required? | Where to get it | Used for |
|----------|-----------|-----------------|----------|
| `SECRET_KEY` | **Yes (production)** | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` | Flask sessions, CSRF |
| `GROQ_API_KEY` | Optional | [console.groq.com](https://console.groq.com) — free, no card | Live AI Goal Coach & check-in summaries |
| `DATABASE_URL` | Production | Host dashboard (Postgres) | Persistent data |
| `FLASK_ENV` | Yes | Set to `production` on host | Security cookies |
| `CYCLE_YEAR` | Optional | Default `2025` | Goal cycle |
| `GEMINI_API_KEY` | Optional backup | Google AI Studio | Only if you switch `AI_PROVIDER=gemini` |

**You do not need:** Azure AD, Teams, or any payment card for the hackathon demo.

---

## Will putting your API key in the repo expose it?

**Yes — never commit `.env` or paste keys in GitHub, README, or frontend code.**

GoalVault is designed so keys stay **server-side only**:

- `GROQ_API_KEY` is read in `ai_service.py` on the server.
- The browser never receives your key.
- Users only call `/api/ai/analyse-goal`; the server adds the key when calling Groq.

### Safe pattern (what you should do)

```
Local:     goalvault/.env          → gitignored
Railway:   Project → Variables     → GROQ_API_KEY=gsk_...
Render:    Environment → Secret      → same
```

### Unsafe (never do this)

- Committing `.env` to GitHub
- Putting `GROQ_API_KEY` in JavaScript or HTML
- Sharing screenshots of Railway variables in slides with real keys visible

If a key is leaked: revoke it at console.groq.com and create a new one.

---

## Production environment checklist

```env
FLASK_ENV=production
SECRET_KEY=<long-random-string>
DATABASE_URL=postgresql://...
GROQ_API_KEY=<your-key>
CYCLE_YEAR=2025
```

Railway/Render inject `PORT` automatically for Gunicorn.

---

## Privacy & data

| Data | Stored where | Notes |
|------|--------------|-------|
| Passwords | Your database (hashed) | bcrypt via Werkzeug |
| Goals & achievements | Your database | You control the host |
| AI prompts | Sent to Groq only when key set | Groq privacy policy applies |
| Audit logs | Your database | Hash-chained, not sent externally |

For a hackathon demo, SQLite locally is fine. Production should use PostgreSQL on the same private network as the app (Railway/Render internal URL).

---

## Post-deploy verification

1. Open live URL → login as all 3 roles.
2. Admin → Audit Trail → Verify Chain → **INTACT**.
3. Employee → Create Goal → AI Coach (with key) or demo mode (without).
4. Admin → Export Excel → download works.
5. Confirm `.env` is **not** in your GitHub repo: `git status` should ignore it.

---

## Demo without any API keys

Leave `GROQ_API_KEY` empty. The app uses built-in demo AI responses — safe for judges and no external calls.
