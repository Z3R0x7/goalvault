# GoalVault

**Set goals with clarity. Track with confidence. Secured by design.**

GoalVault is a security-first, AI-assisted goal intelligence platform built for **AtomQuest Hackathon 1.0** — an in-house Goal Setting & Tracking Portal.

## Highlights

- Full **Phase 1 & 2** workflows: goal creation, manager approval, quarterly achievements, check-ins
- **Hash-chained audit trail** — tamper-evident logging with one-click integrity verification
- **AI Goal Coach** (Groq / Llama 3.1) — SMART analysis and manager check-in summaries
- **Role-based access**: Employee, Manager (L1), Admin/HR
- **Escalation module**, Excel export, completion dashboard
- Demo-ready with seeded accounts

## Quick Start

See **[HOW_TO_RUN.md](HOW_TO_RUN.md)** for full setup instructions.

```bash
cd goalvault
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add GROQ_API_KEY when ready
python seed_data.py
python run.py
```

Visit http://localhost:8080

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Employee | employee@goalvault.com | Demo@123 |
| Manager | manager@goalvault.com | Demo@123 |
| Admin | admin@goalvault.com | Demo@123 |

## Tech Stack

- **Backend:** Python Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend:** Bootstrap 5, Jinja2, Chart.js-ready layout
- **AI:** Groq API (Llama 3.1 70B) — optional, demo mode without key
- **Database:** SQLite (dev) / PostgreSQL (production)

## License

Built for AtomQuest Hackathon 1.0.
