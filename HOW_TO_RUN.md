# AtomQuest — GoalVault

Full app is in **`goalvault/`**. See also **`goalvault/DEPLOYMENT.md`** for hosting and API key security.

## Run locally

```bash
cd goalvault
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python run.py
```

Open http://localhost:8080 — password for all roles: **Demo@123**

| Role | Email |
|------|-------|
| Employee | employee@goalvault.com |
| Manager | manager@goalvault.com |
| Admin | admin@goalvault.com |

## API keys (your side)

| Key | Required | Purpose |
|-----|----------|---------|
| `SECRET_KEY` | Production only | Sessions |
| `GROQ_API_KEY` | Optional | Live AI (demo works without it) |

Set in `goalvault/.env` — never commit this file. On Railway/Render, use the dashboard **Environment Variables** tab.

## Host for judges

Recommended: **Railway** or **Render** — steps in `goalvault/DEPLOYMENT.md`.

## Upload to GitHub

From the `Aatomquest` folder (repo root):

```bash
python scripts/push_to_github.py --dry-run
python scripts/push_to_github.py -m "Initial commit: GoalVault" --create-repo --repo goalvault
```

Requires `git` and `gh auth login`. See [README.md](README.md) for details.
