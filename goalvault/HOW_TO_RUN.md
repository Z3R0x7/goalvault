# How to Run GoalVault

GoalVault is the AtomQuest Hackathon 1.0 submission — a security-first goal setting and tracking portal.

## Prerequisites

- Python 3.10 or newer
- pip

## Quick Start (Local Demo)

### 1. Open the project folder

```bash
cd goalvault
```

### 2. Create and activate a virtual environment

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example env file (if you do not already have `.env`):

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

| Variable | Required | Notes |
|----------|----------|-------|
| `SECRET_KEY` | Yes | Any random string for sessions |
| `GROQ_API_KEY` | Optional | Leave empty for demo AI responses; add key from [console.groq.com](https://console.groq.com) for live AI |
| `DATABASE_URL` | No | Defaults to `sqlite:///goalvault.db` |

### 5. Seed the demo database

```bash
python seed_data.py
```

This creates three demo users and sample goals with audit log entries.

### 6. Start the application

```bash
python run.py
```

Open **http://localhost:8080** in your browser.

## Demo Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Employee | employee@goalvault.com | Demo@123 |
| Manager | manager@goalvault.com | Demo@123 |
| Admin | admin@goalvault.com | Demo@123 |

## Demo Walkthrough (8–10 minutes)

### Employee (3 min)

1. Sign in as **employee@goalvault.com**
2. Open **Dashboard** — review goal summary cards
3. **Create Goal** — fill in fields, click **Analyse My Goal** (AI Coach sidebar)
4. Submit a draft goal for approval
5. Open **Q1 Achievement** on an approved goal

### Manager (2.5 min)

1. Sign in as **manager@goalvault.com**
2. Open **Approvals** — approve or return a submitted goal
3. Open **Team** → **Q1 Check-in** — click **Generate AI Summary**

### Admin (3 min)

1. Sign in as **admin@goalvault.com**
2. Open **Completion Dashboard** and **Cycle Config**
3. Open **Audit Trail** → **Verify Chain Integrity** (green = intact)
4. **Export Excel Report** from the admin dashboard
5. **Security** → **Trigger Escalation Check Now**

### Audit trail tamper demo (optional)

1. Open the SQLite DB (`goalvault.db`) with any SQLite browser
2. Change any value in the `audit_logs` table
3. In Admin → Audit Trail, click **Verify Chain Integrity** again — broken chain is detected

## AI Features

- Without `GROQ_API_KEY`: the app runs in **demo mode** with sample AI feedback
- With `GROQ_API_KEY`: live Llama 3.1 analysis via Groq (free tier)

## Production / Deployment

```bash
pip install gunicorn
export FLASK_ENV=production
export DATABASE_URL=postgresql://...   # optional
python seed_data.py
gunicorn run:app --bind 0.0.0.0:5000
```

Or use the included `Procfile` on Railway / Render.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Activate venv and run `pip install -r requirements.txt` |
| Database errors | Delete `goalvault.db` and run `python seed_data.py` again |
| Port 8080 in use | Set `PORT=8081 python run.py` |
| AI returns demo text | Add `GROQ_API_KEY` to `.env` and restart |

## Project Structure

```
goalvault/
├── app/           # Flask application (routes, models, templates)
├── seed_data.py   # Demo data loader
├── run.py         # Entry point
├── config.py      # Configuration
├── requirements.txt
└── .env           # Your secrets (not committed)
```
