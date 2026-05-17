# AtomQuest Hackathon 1.0 — Full Development Plan
## "GoalVault" — Security-First Goal Intelligence Platform

---

## Table of Contents
1. [Project Identity & Pitch](#1-project-identity--pitch)
2. [Free AI Stack Decision](#2-free-ai-stack-decision)
3. [Full Tech Stack](#3-full-tech-stack)
4. [System Architecture](#4-system-architecture)
5. [Database Schema](#5-database-schema)
6. [Project Folder Structure](#6-project-folder-structure)
7. [Phase-by-Phase Development Plan](#7-phase-by-phase-development-plan)
8. [Feature Implementation Details](#8-feature-implementation-details)
9. [Security Implementation Details](#9-security-implementation-details)
10. [AI Feature Implementation](#10-ai-feature-implementation)
11. [Demo Script](#11-demo-script)
12. [Architecture Diagram Description](#12-architecture-diagram-description)
13. [Setup & Run Instructions](#13-setup--run-instructions)

---

## 1. Project Identity & Pitch

**Product Name:** GoalVault

**Tagline:** *"Set goals with clarity. Track with confidence. Secured by design."*

**One-line pitch for judges:**
> While every other team built a goal tracker, we built a **tamper-proof, security-hardened, AI-assisted goal intelligence platform** — the only submission where you can *prove* no one touched the data.

**What makes it memorable:**
- The hash-chained audit trail is a live demo moment — show the chain, snap it, show the alert. No other team will have this.
- The AI Goal Coach is embedded in the workflow, not bolted on. It shows when writing goals — judges see it in action.
- The UI is clean, role-differentiated, and designed for non-technical users (scoring criterion #3).

---

## 2. Free AI Stack Decision

### Chosen: Groq API (Free Tier)

**Why Groq over other free options:**

| Option | Free Tier | Speed | Model Quality | Hackathon Suitability |
|---|---|---|---|---|
| **Groq** | ✅ Generous (14,400 req/day) | ⚡ Fastest (200+ tokens/sec) | Llama 3.1 70B | ⭐⭐⭐⭐⭐ |
| Google Gemini | ✅ Free (1M tokens/day Flash) | Fast | Gemini 1.5 Flash | ⭐⭐⭐⭐ |
| Hugging Face Inference | ✅ Free but throttled | Slow | Variable | ⭐⭐ |
| Ollama (local) | ✅ Fully free | Hardware-dependent | Llama 3 | ⭐⭐⭐ (no internet dependency) |

**Groq wins because:**
- Speed is *visibly impressive* in live demos — responses appear almost instantly
- Free tier is more than enough for a hackathon (14,400 requests/day)
- Llama 3.1 70B is production-grade quality
- Simple REST API, similar to OpenAI/Anthropic — easy integration

**Backup:** Google Gemini 1.5 Flash — if Groq is down during demo, switch the `AI_PROVIDER` env var and the service layer handles the rest.

### Groq Setup
```
1. Sign up at console.groq.com
2. Generate API key (free, no credit card needed)
3. Set GROQ_API_KEY in .env
4. Model: llama-3.1-70b-versatile
```

---

## 3. Full Tech Stack

### Backend
| Component | Technology | Reason |
|---|---|---|
| Web Framework | **Python Flask 3.x** | Required preference; lightweight, fast to build |
| ORM | **SQLAlchemy 2.x** | Clean models, migration support |
| DB Migrations | **Flask-Migrate (Alembic)** | Version-controlled schema changes |
| Authentication | **Flask-Login + PyJWT** | Session management + API token support |
| Password Hashing | **Werkzeug (bcrypt)** | Industry standard |
| Form Validation | **WTForms + Flask-WTF** | CSRF protection built in |
| Rate Limiting | **Flask-Limiter** | Prevents brute-force on auth endpoints |
| Job Scheduling | **APScheduler** | Runs escalation checks and deadline reminders |
| CSV/Excel Export | **pandas + openpyxl** | Achievement report export |
| CORS | **Flask-CORS** | For AJAX calls from the frontend |
| Environment Config | **python-dotenv** | Secrets management |

### Database
| Environment | Database | Reason |
|---|---|---|
| Development | **SQLite** | Zero setup, file-based |
| Production/Demo | **PostgreSQL** | Robust, free on Railway/Render |

### Frontend
| Component | Technology | Reason |
|---|---|---|
| CSS Framework | **Bootstrap 5.3** | Fast to build, professional, accessible |
| Icons | **Bootstrap Icons** | No CDN dependency issues |
| Charts | **Chart.js** | Lightweight, looks great, free |
| AJAX | **Vanilla Fetch API** | No jQuery dependency |
| Templates | **Jinja2** | Native to Flask |

### AI Layer
| Component | Technology |
|---|---|
| AI Provider | **Groq API (free)** |
| Model | **llama-3.1-70b-versatile** |
| Backup Provider | **Google Gemini 1.5 Flash (free)** |
| Integration | **requests library** (no SDK needed) |

### Security Layer (Your Differentiator)
| Feature | Implementation |
|---|---|
| Audit Trail | **Hash-chained SHA-256 log** |
| Input Sanitization | **bleach library + WTForms validators** |
| CSRF Protection | **Flask-WTF CSRF tokens** |
| Session Security | **HTTPOnly + Secure cookie flags** |
| Auth Logging | **Failed login attempt tracking** |
| XSS Prevention | **Jinja2 auto-escaping + CSP headers** |
| SQL Injection | **SQLAlchemy parameterized queries** |

### DevOps & Deployment
| Component | Tool |
|---|---|
| Version Control | **Git + GitHub** |
| Hosting | **Railway.app or Render.com (free tier)** |
| DB Hosting | **Railway PostgreSQL (free)** |
| Environment | **python-dotenv** |
| Process Manager | **Gunicorn** |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (User)                        │
│              Bootstrap 5 + Jinja2 Templates                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / AJAX (Fetch API)
┌──────────────────────▼──────────────────────────────────────┐
│                    Flask Application                          │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Auth Routes  │  │ Role Routes  │  │   API Routes      │  │
│  │ /auth/*      │  │ /employee/*  │  │   /api/ai/*       │  │
│  │              │  │ /manager/*   │  │   /api/export/*   │  │
│  │              │  │ /admin/*     │  │                   │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬──────────┘  │
│         │                 │                    │             │
│  ┌──────▼─────────────────▼────────────────────▼──────────┐ │
│  │                  Service Layer                           │ │
│  │  AuditService │ AIService │ ExportService │ Escalation  │ │
│  └──────────────────────┬───────────────────────────────── ┘ │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────────┐ │
│  │              SQLAlchemy ORM (Models)                     │ │
│  │  User │ Goal │ SharedGoal │ Achievement │ AuditLog       │ │
│  └──────────────────────┬───────────────────────────────── ┘ │
└─────────────────────────┼────────────────────────────────────┘
                          │
         ┌────────────────┴────────────────┐
         │                                 │
┌────────▼────────┐               ┌────────▼────────┐
│   SQLite / PG   │               │   Groq API      │
│   Database      │               │   (Llama 3.1)   │
└─────────────────┘               └─────────────────┘
```

### Request Flow (Example: Employee submits goal)
```
1. Employee fills goal form → POST /employee/goals/create
2. Flask-WTF validates CSRF token
3. Flask-Login confirms role = EMPLOYEE
4. WTForms validates fields (weightage, UoM, etc.)
5. Service layer checks business rules (total ≤ 100%, max 8 goals)
6. SQLAlchemy writes Goal to DB
7. AuditService creates hash-chained log entry
8. Response returns → Jinja2 renders success page
```

---

## 5. Database Schema

### Table: users
```sql
id              INTEGER PRIMARY KEY
name            VARCHAR(100) NOT NULL
email           VARCHAR(150) UNIQUE NOT NULL
password_hash   VARCHAR(256) NOT NULL
role            ENUM('employee', 'manager', 'admin') NOT NULL
manager_id      INTEGER FK → users.id (NULL for managers/admin)
department      VARCHAR(100)
is_active       BOOLEAN DEFAULT TRUE
created_at      DATETIME
last_login      DATETIME
failed_logins   INTEGER DEFAULT 0
```

### Table: goals
```sql
id              INTEGER PRIMARY KEY
employee_id     INTEGER FK → users.id
thrust_area     VARCHAR(100)
title           VARCHAR(200)
description     TEXT
uom_type        ENUM('numeric_min', 'numeric_max', 'timeline', 'zero')
target          FLOAT
weightage       FLOAT  -- must total 100% per employee
status          ENUM('draft', 'submitted', 'approved', 'rework', 'locked')
is_shared       BOOLEAN DEFAULT FALSE
shared_from_id  INTEGER FK → goals.id (NULL if original)
cycle_year      INTEGER
created_at      DATETIME
updated_at      DATETIME
locked_at       DATETIME
```

### Table: achievements
```sql
id              INTEGER PRIMARY KEY
goal_id         INTEGER FK → goals.id
quarter         ENUM('Q1', 'Q2', 'Q3', 'Q4')
actual_value    FLOAT
status          ENUM('not_started', 'on_track', 'completed')
progress_score  FLOAT  -- system-computed
submitted_at    DATETIME
manager_comment TEXT
checkin_at      DATETIME
```

### Table: audit_logs (The Differentiator)
```sql
id              INTEGER PRIMARY KEY
timestamp       DATETIME NOT NULL
user_id         INTEGER FK → users.id
action          VARCHAR(100)  -- e.g., 'GOAL_LOCKED', 'GOAL_EDITED'
entity_type     VARCHAR(50)   -- e.g., 'goal', 'achievement'
entity_id       INTEGER
old_value       TEXT (JSON)
new_value       TEXT (JSON)
ip_address      VARCHAR(45)
prev_hash       VARCHAR(64)   -- SHA-256 of previous log entry
entry_hash      VARCHAR(64)   -- SHA-256 of this entry's content
```

### Table: escalations
```sql
id              INTEGER PRIMARY KEY
rule_type       ENUM('goal_not_submitted', 'goal_not_approved', 'checkin_missed')
triggered_at    DATETIME
target_user_id  INTEGER FK → users.id
notified_at     DATETIME
resolved        BOOLEAN DEFAULT FALSE
```

### Table: cycle_config (Admin configures)
```sql
id              INTEGER PRIMARY KEY
cycle_year      INTEGER
phase           ENUM('goal_setting', 'Q1', 'Q2', 'Q3', 'Q4')
window_open     DATE
window_close    DATE
escalation_days INTEGER  -- days before escalation fires
```

---

## 6. Project Folder Structure

```
goalvault/
│
├── app/
│   ├── __init__.py              # App factory, register blueprints
│   ├── extensions.py            # db, login_manager, limiter, scheduler
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model + role enum
│   │   ├── goal.py              # Goal model + shared goal logic
│   │   ├── achievement.py       # Achievement + progress score calc
│   │   ├── audit_log.py         # Hash-chained audit log model
│   │   ├── escalation.py        # Escalation rules + log
│   │   └── cycle_config.py      # Cycle window config
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # /auth/login, /auth/logout, /auth/register
│   │   ├── employee.py          # /employee/* — goal creation, achievements
│   │   ├── manager.py           # /manager/* — approvals, check-ins, team view
│   │   ├── admin.py             # /admin/* — cycle config, audit view, user mgmt
│   │   └── api.py               # /api/* — AI endpoint, export endpoint
│   │
│   ├── services/
│   │   ├── audit_service.py     # Hash-chain logic, log writer
│   │   ├── ai_service.py        # Groq API calls, prompt templates
│   │   ├── export_service.py    # pandas CSV/Excel export
│   │   ├── escalation_service.py# APScheduler jobs, rule evaluation
│   │   └── goal_service.py      # Business rules (weightage, max goals)
│   │
│   ├── templates/
│   │   ├── base.html            # Master layout, navbar, flash messages
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── register.html
│   │   ├── employee/
│   │   │   ├── dashboard.html
│   │   │   ├── goal_create.html  # AI Goal Coach sidebar lives here
│   │   │   ├── goal_list.html
│   │   │   └── achievement.html
│   │   ├── manager/
│   │   │   ├── dashboard.html
│   │   │   ├── team_goals.html
│   │   │   ├── approval.html
│   │   │   └── checkin.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── audit_trail.html  # Hash-chain visualizer
│   │       ├── users.html
│   │       ├── cycle_config.html
│   │       ├── completion.html
│   │       └── security.html     # Failed logins, active sessions
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── goalvault.css    # Custom styles on top of Bootstrap
│   │   ├── js/
│   │   │   ├── goal_form.js     # Real-time weightage validator
│   │   │   ├── ai_coach.js      # AI Goal Coach AJAX calls
│   │   │   └── audit_chain.js   # Visual hash-chain renderer
│   │   └── img/
│   │
│   └── utils/
│       ├── decorators.py        # @role_required decorator
│       ├── validators.py        # Business rule validators
│       └── security_headers.py  # CSP, X-Frame-Options headers
│
├── migrations/                  # Alembic migrations (auto-generated)
├── tests/
│   ├── test_auth.py
│   ├── test_goals.py
│   ├── test_audit.py
│   └── test_ai.py
│
├── seed_data.py                 # Seed DB with 3 demo users + sample goals
├── config.py                    # Dev/Prod config classes
├── requirements.txt
├── .env.example
├── Procfile                     # For Railway/Render deployment
├── README.md
└── run.py                       # Entry point
```

---

## 7. Phase-by-Phase Development Plan

> Estimated hackathon duration: 24 hours (adjust if different)
> Team: Solo or small team

---

### PHASE 0 — Setup (Hour 0–1)

**Goal:** Working skeleton, zero functionality gaps later due to config issues.

**Steps:**
1. Create GitHub repo, clone locally
2. Create virtualenv: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install flask flask-sqlalchemy flask-migrate flask-login flask-wtf flask-limiter flask-cors apscheduler pandas openpyxl requests python-dotenv bleach gunicorn`
4. Create `requirements.txt`: `pip freeze > requirements.txt`
5. Create `config.py` with Dev/Prod classes
6. Create `app/__init__.py` with app factory pattern
7. Create `app/extensions.py` (db, login_manager, limiter)
8. Test: `flask run` shows blank 200 OK
9. Initialize Flask-Migrate: `flask db init`
10. Set up `.env` with `GROQ_API_KEY`, `SECRET_KEY`, `DATABASE_URL`

**Deliverable:** App boots, git repo initialized, .env configured

---

### PHASE 1 — Models + DB (Hour 1–3)

**Goal:** All tables created, relationships correct, seed data ready.

**Steps:**
1. Write `models/user.py` — User model with role enum, password hash methods
2. Write `models/goal.py` — Goal model, shared goal FK, status enum
3. Write `models/achievement.py` — Achievement + `compute_progress_score()` method
4. Write `models/audit_log.py` — Hash-chain model (see Section 9 for detail)
5. Write `models/escalation.py` and `models/cycle_config.py`
6. Run `flask db migrate -m "initial schema"` then `flask db upgrade`
7. Write `seed_data.py`:
   - Admin: admin@goalvault.com / Admin@123
   - Manager: manager@goalvault.com / Manager@123
   - Employee: employee@goalvault.com / Employee@123
   - Pre-populate 3 goals for employee (approved), 1 pending approval, Q1 achievements
8. Run `python seed_data.py` and verify in SQLite browser

**Deliverable:** DB tables exist, seed data loads cleanly, relationships verified

---

### PHASE 2 — Authentication (Hour 3–5)

**Goal:** Login/logout works for all 3 roles, role-based redirect on login.

**Steps:**
1. Write `utils/decorators.py` — `@role_required('manager')` decorator
2. Write `routes/auth.py`:
   - `GET/POST /auth/login` — WTForms login form, CSRF protected
   - `POST /auth/logout` — clears session
   - Track `failed_logins` counter, lock after 5 attempts
3. Configure `login_manager` in extensions — `login_view = 'auth.login'`
4. Write `templates/auth/login.html` — clean Bootstrap form
5. On login success, redirect by role:
   - employee → `/employee/dashboard`
   - manager → `/manager/dashboard`
   - admin → `/admin/dashboard`
6. Apply Flask-Limiter: `@limiter.limit("5 per minute")` on login route
7. Log every login attempt to AuditLog

**Deliverable:** All 3 demo accounts can log in/out, role redirect works, brute force protection active

---

### PHASE 3 — Employee Goal Workflow (Hour 5–9)

**Goal:** Full Phase 1 employee side — create, submit, view locked goals.

**Steps:**
1. Write `services/goal_service.py`:
   - `validate_weightage(employee_id, new_goal_weightage)` — checks total ≤ 100%, min 10%
   - `count_goals(employee_id)` — checks max 8
   - `is_window_open('goal_setting')` — checks CycleConfig dates
2. Write `routes/employee.py`:
   - `GET /employee/dashboard` — shows goals summary, progress bars
   - `GET /employee/goals` — lists all goals with status badges
   - `GET/POST /employee/goals/create` — goal creation form
   - `POST /employee/goals/<id>/submit` — submit for approval
   - `GET/POST /employee/goals/<id>/edit` — edit draft goals only
   - `GET/POST /employee/achievement/<id>` — quarterly achievement input
3. Write `templates/employee/goal_create.html`:
   - Form fields: Thrust Area, Title, Description, UoM, Target, Weightage
   - **Live weightage meter** (JS) — shows remaining % in real time
   - **AI Coach sidebar** — "Analyse My Goal" button (Phase 10)
4. Write `templates/employee/dashboard.html`:
   - Cards: Total Goals, Approved, Pending, Avg Progress Score
   - Goal list with status badges and quarter progress
5. Enforce: locked goals show read-only view, no edit route accessible
6. Write `templates/employee/achievement.html`:
   - Per-goal: actual value input, status dropdown
   - Show planned vs. actual comparison

**Deliverable:** Employee can create goals (with validation), submit them, update quarterly achievements

---

### PHASE 4 — Manager Workflow (Hour 9–12)

**Goal:** Manager can view team, approve/return goals, add check-in comments.

**Steps:**
1. Write `routes/manager.py`:
   - `GET /manager/dashboard` — team summary cards, pending approvals count
   - `GET /manager/team` — list all direct reports + their goal status
   - `GET /manager/approvals` — list pending submissions
   - `POST /manager/goals/<id>/approve` — approve + lock goal
   - `POST /manager/goals/<id>/return` — return for rework with comment
   - `GET/POST /manager/checkin/<employee_id>` — quarterly check-in module
2. Write `templates/manager/approval.html`:
   - Side-by-side: submitted goal vs. editable fields (target/weightage)
   - Inline edit capability before approval
   - Approve / Return buttons with confirmation modal
3. Write `templates/manager/team_goals.html`:
   - Table: Employee | Goals | Status | Q1 | Q2 | Q3 | Q4 progress
   - Filterable by department, status
4. Write `templates/manager/checkin.html`:
   - Shows Planned Target vs. Actual Achievement per goal
   - Text area for structured Check-in Comment
   - Submit locks the check-in for that quarter
5. On approval, call `AuditService.log('GOAL_APPROVED', goal_id, ...)`

**Deliverable:** Manager can approve goals (locks them), return for rework, complete quarterly check-ins

---

### PHASE 5 — Admin Workflow (Hour 12–15)

**Goal:** Admin has full control — cycle config, user management, audit trail viewer.

**Steps:**
1. Write `routes/admin.py`:
   - `GET /admin/dashboard` — completion rates, org-wide progress
   - `GET/POST /admin/users` — list users, add user, toggle active
   - `GET/POST /admin/cycle-config` — set window open/close dates per phase
   - `GET /admin/audit-trail` — paginated hash-chain log with verify button
   - `GET /admin/completion` — real-time check-in completion dashboard
   - `POST /admin/goals/<id>/unlock` — exception handling (unlock locked goal)
   - `GET /admin/security` — failed logins, escalation log
2. Write `templates/admin/audit_trail.html`:
   - Table: Timestamp | User | Action | Entity | Old Value | New Value | Hash
   - "Verify Chain Integrity" button → calls `/api/audit/verify`
   - Visual indicator: green chain links if intact, red broken link if tampered
3. Write `templates/admin/completion.html`:
   - Real-time dashboard: % employees submitted, % managers approved, % check-ins done
4. Write `templates/admin/cycle_config.html`:
   - Form to set window dates for Goal Setting, Q1, Q2, Q3, Q4
   - Escalation day threshold per phase
5. Write `templates/admin/security.html`:
   - Table of failed login attempts with IP, timestamp, user
   - Active sessions count

**Deliverable:** Admin has full oversight, audit trail is viewable and verifiable, cycle dates configurable

---

### PHASE 6 — Reporting & Export (Hour 15–16)

**Goal:** CSV/Excel export + completion dashboard working.

**Steps:**
1. Write `services/export_service.py`:
   - `generate_achievement_report(cycle_year)` using pandas DataFrame
   - Columns: Employee | Dept | Goal Title | UoM | Target | Q1 Actual | Q2 Actual | Q3 Actual | Q4 Actual | Progress Score
   - Export as Excel (.xlsx) with openpyxl formatting
2. Add export route in `routes/api.py`:
   - `GET /api/export/achievement-report?year=2025` → streams Excel file
3. Add "Export Report" button to Admin dashboard

**Deliverable:** Admin can download formatted Excel achievement report

---

### PHASE 7 — Security Layer (Hour 16–18)

**Goal:** All security features wired in — this is your differentiator.

**Steps:**
1. Write `services/audit_service.py` — full hash-chain implementation (see Section 9)
2. Write `utils/security_headers.py` — add CSP, X-Content-Type, X-Frame-Options headers
3. Ensure all forms have CSRF tokens (Flask-WTF handles this)
4. Audit all routes: confirm `@login_required` + `@role_required` on every route
5. Audit all DB queries: confirm no raw SQL (all ORM)
6. Add bleach sanitization on any text field that renders in HTML
7. Add `/api/audit/verify` endpoint — verifies entire chain, returns JSON result
8. Wire up the Admin audit trail "Verify Chain" button to this endpoint

**Deliverable:** Hash-chain audit works end-to-end, chain verify demo works, security headers active

---

### PHASE 8 — AI Goal Coach (Hour 18–20)

**Goal:** AI feature is visible, useful, and smooth in the demo.

**Steps:** (See full detail in Section 10)
1. Write `services/ai_service.py` — Groq API wrapper
2. Write prompt templates for:
   - Goal quality check (SMART analysis)
   - Weightage balance advice
   - Check-in summary for manager
3. Add `/api/ai/analyse-goal` POST endpoint
4. Wire AI Coach sidebar in `goal_create.html`
5. Wire AI Summary button in manager check-in view
6. Test with 3-4 real goal examples

**Deliverable:** AI feature works live, adds visible value in employee and manager flows

---

### PHASE 9 — Escalation Module (Hour 20–21)

**Goal:** Background scheduler checks rules and marks escalations.

**Steps:**
1. Write `services/escalation_service.py`:
   - `check_goal_not_submitted()` — employees past window open with no submission
   - `check_goal_not_approved()` — submissions pending past N days
   - `check_checkin_missed()` — active quarter, no check-in submitted
2. Register APScheduler job in `app/__init__.py` — runs daily at 8am
3. Escalation records are visible in Admin security dashboard
4. For demo: add a "Trigger Escalation Check Now" button in Admin panel

**Deliverable:** Escalation module works, visible in admin panel, impressive for bonus points

---

### PHASE 10 — Polish, Deploy, Seed (Hour 21–24)

**Goal:** Live URL, demo accounts ready, no broken flows.

**Steps:**
1. UI pass: consistent spacing, no broken Bootstrap classes, mobile responsive
2. Flash messages on all success/error actions
3. 404 and 500 error pages
4. Run through full demo script for each role (see Section 11)
5. Fix any broken flows found during demo run-through
6. Deploy to Railway or Render:
   - Add `Procfile`: `web: gunicorn run:app`
   - Push to GitHub
   - Connect Railway to GitHub repo
   - Set env vars in Railway dashboard
   - Run `flask db upgrade` on production
   - Run seed data on production
7. Verify live URL works for all 3 role journeys
8. Write architecture diagram (draw.io or excalidraw)
9. Submit GitHub repo + live URL + credentials

---

## 8. Feature Implementation Details

### 8.1 Weightage Validation (Real-time JS)

```javascript
// static/js/goal_form.js
function updateWeightageBar() {
    const allGoalWeightages = existingGoalsTotal; // pre-loaded from Jinja
    const currentInput = parseFloat(document.getElementById('weightage').value) || 0;
    const total = allGoalWeightages + currentInput;
    const remaining = 100 - allGoalWeightages;

    const bar = document.getElementById('weightage-bar');
    bar.style.width = total + '%';
    bar.className = total > 100 ? 'progress-bar bg-danger' : 
                    total === 100 ? 'progress-bar bg-success' : 'progress-bar bg-primary';
    
    document.getElementById('weightage-remaining').textContent = 
        `${remaining - currentInput}% remaining`;

    // Block submit if invalid
    document.getElementById('submit-btn').disabled = 
        total > 100 || currentInput < 10 || total === 0;
}
```

### 8.2 Progress Score Computation

```python
# models/achievement.py
def compute_progress_score(self):
    goal = self.goal
    if goal.uom_type == 'numeric_min':
        return min((self.actual_value / goal.target) * 100, 100) if goal.target else 0
    elif goal.uom_type == 'numeric_max':
        return min((goal.target / self.actual_value) * 100, 100) if self.actual_value else 0
    elif goal.uom_type == 'zero':
        return 100.0 if self.actual_value == 0 else 0.0
    elif goal.uom_type == 'timeline':
        # Returns 100% if completed by deadline, else proportional
        if self.completion_date and goal.target_date:
            if self.completion_date <= goal.target_date:
                return 100.0
            else:
                delta = (self.completion_date - goal.target_date).days
                return max(0, 100 - (delta * 10))  # -10% per day late
    return 0.0
```

### 8.3 Shared Goals Logic

When admin pushes a shared goal:
- Original goal is created with `is_shared=True`, `shared_owner_id = admin`
- For each target employee, a copy is created with `shared_from_id = original_goal.id`
- Recipient can only edit `weightage` — Title and Target fields are read-only
- When the primary owner updates achievement → a background job syncs `actual_value` to all linked copies

---

## 9. Security Implementation Details

### 9.1 Hash-Chained Audit Trail

This is your standout feature. Every change to a locked goal creates an audit log entry whose hash depends on the previous entry. Tampering with any entry breaks the chain — and the system detects it.

```python
# services/audit_service.py
import hashlib
import json
from datetime import datetime
from app.models.audit_log import AuditLog
from app import db

class AuditService:

    @staticmethod
    def _compute_hash(entry_data: dict, prev_hash: str) -> str:
        """SHA-256 of entry content + previous hash = tamper-evident chain"""
        payload = json.dumps(entry_data, sort_keys=True, default=str) + prev_hash
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def log(action: str, entity_type: str, entity_id: int,
            user_id: int, old_value=None, new_value=None, ip_address=None):
        
        # Get the hash of the last entry (or genesis hash if first)
        last_entry = AuditLog.query.order_by(AuditLog.id.desc()).first()
        prev_hash = last_entry.entry_hash if last_entry else "GENESIS"
        
        entry_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "old_value": old_value,
            "new_value": new_value,
            "ip_address": ip_address
        }
        
        entry_hash = AuditService._compute_hash(entry_data, prev_hash)
        
        log = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=json.dumps(old_value),
            new_value=json.dumps(new_value),
            ip_address=ip_address,
            prev_hash=prev_hash,
            entry_hash=entry_hash
        )
        db.session.add(log)
        db.session.commit()

    @staticmethod
    def verify_chain() -> dict:
        """Walk the entire audit log and verify each hash. Returns integrity report."""
        entries = AuditLog.query.order_by(AuditLog.id.asc()).all()
        prev_hash = "GENESIS"
        broken_at = None
        
        for entry in entries:
            entry_data = {
                "timestamp": entry.timestamp.isoformat(),
                "user_id": entry.user_id,
                "action": entry.action,
                "entity_type": entry.entity_type,
                "entity_id": entry.entity_id,
                "old_value": json.loads(entry.old_value) if entry.old_value else None,
                "new_value": json.loads(entry.new_value) if entry.new_value else None,
                "ip_address": entry.ip_address
            }
            expected_hash = AuditService._compute_hash(entry_data, prev_hash)
            
            if expected_hash != entry.entry_hash:
                broken_at = entry.id
                break
            prev_hash = entry.entry_hash
        
        return {
            "intact": broken_at is None,
            "total_entries": len(entries),
            "broken_at_id": broken_at,
            "message": "Chain intact ✓" if broken_at is None else f"Chain broken at entry #{broken_at} ✗"
        }
```

**Demo moment:** Open SQLite browser → manually change a value in the audit_log table → go to Admin panel → click "Verify Chain Integrity" → system detects tamper and highlights the broken link in red.

### 9.2 Role-Based Access Decorator

```python
# utils/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage:
# @role_required('manager', 'admin')
# def team_dashboard(): ...
```

### 9.3 Security Headers

```python
# utils/security_headers.py
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net; "
    )
    return response
```

---

## 10. AI Feature Implementation

### What it does (3 use cases)

**Use Case 1: AI Goal Coach (Employee flow)**
When writing a goal, employee clicks "Analyse My Goal" →
AI checks if the goal is specific, measurable, and appropriate for the UoM selected.
Returns: quality score + 2-3 specific improvement suggestions.

**Use Case 2: Weightage Advisor**
After entering weightage, AI checks if the distribution makes sense relative to other goals and suggests rebalancing if one goal dominates too much.

**Use Case 3: Check-in Summarizer (Manager flow)**
After viewing a team member's quarterly achievements, manager clicks "Generate Summary" →
AI creates a structured check-in comment the manager can edit and save.

### Implementation

```python
# services/ai_service.py
import os
import requests
import json

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-70b-versatile"

class AIService:
    
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    @staticmethod
    def analyse_goal(title: str, description: str, uom_type: str, target: float) -> dict:
        prompt = f"""
You are a professional performance management consultant reviewing an employee goal.

Goal Title: {title}
Description: {description}
Unit of Measurement: {uom_type}
Target: {target}

Analyse this goal and respond ONLY with valid JSON in this exact format:
{{
    "quality_score": <integer 1-10>,
    "is_smart": <true/false>,
    "issues": [<list of specific issues, max 3>],
    "suggestions": [<list of concrete improvements, max 3>],
    "uom_appropriate": <true/false>,
    "uom_comment": "<one sentence on UoM fit>"
}}
No preamble. No markdown. Only the JSON object.
"""
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 400
        }
        try:
            r = requests.post(GROQ_API_URL, headers=AIService.headers, 
                            json=payload, timeout=10)
            content = r.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "quality_score": 0}

    @staticmethod
    def generate_checkin_comment(employee_name: str, goals_summary: list) -> str:
        goals_text = "\n".join([
            f"- {g['title']}: Planned {g['target']}, Achieved {g['actual']}, Status: {g['status']}"
            for g in goals_summary
        ])
        prompt = f"""
Write a professional, concise quarterly check-in comment for {employee_name}'s performance review.

Goals progress:
{goals_text}

Write 3-4 sentences that: acknowledge achievements, note areas needing attention, and suggest a next step.
Keep it factual and constructive. Plain text only, no bullet points.
"""
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 200
        }
        try:
            r = requests.post(GROQ_API_URL, headers=AIService.headers,
                            json=payload, timeout=10)
            return r.json()["choices"][0]["message"]["content"].strip()
        except:
            return "Unable to generate summary. Please write manually."
```

### Frontend Integration (AI Coach Sidebar)

```javascript
// static/js/ai_coach.js
async function analyseGoal() {
    const btn = document.getElementById('ai-analyse-btn');
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analysing...';
    btn.disabled = true;

    const payload = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        uom_type: document.getElementById('uom_type').value,
        target: document.getElementById('target').value
    };

    const res = await fetch('/api/ai/analyse-goal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json',
                  'X-CSRFToken': document.querySelector('[name=csrf_token]').value},
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    renderAIResult(data);
    btn.innerHTML = '✦ Analyse My Goal';
    btn.disabled = false;
}

function renderAIResult(data) {
    const panel = document.getElementById('ai-result-panel');
    const score = data.quality_score;
    const color = score >= 7 ? 'success' : score >= 4 ? 'warning' : 'danger';
    
    panel.innerHTML = `
        <div class="d-flex align-items-center mb-2">
            <span class="badge bg-${color} fs-5 me-2">${score}/10</span>
            <strong>Goal Quality Score</strong>
        </div>
        ${data.issues.length ? `
        <p class="text-danger mb-1"><strong>Issues:</strong></p>
        <ul>${data.issues.map(i => `<li>${i}</li>`).join('')}</ul>` : ''}
        <p class="text-success mb-1"><strong>Suggestions:</strong></p>
        <ul>${data.suggestions.map(s => `<li>${s}</li>`).join('')}</ul>
        <small class="text-muted">UoM: ${data.uom_comment}</small>
    `;
    panel.style.display = 'block';
}
```

---

## 11. Demo Script

**Total demo time target: 8–10 minutes**

### Role 1 — Employee (3 min)
1. Log in as employee@goalvault.com
2. Show dashboard — explain the progress cards
3. Click "Create New Goal" — fill in a goal with AI Coach sidebar visible
4. Type goal details → click "Analyse My Goal" → AI response appears in sidebar
5. Adjust goal based on AI feedback (this is your "wow" moment)
6. Submit second goal, show weightage meter hitting 100%
7. Submit goals for approval → status changes to "Submitted"
8. Show Q1 achievement entry against an approved goal

### Role 2 — Manager (2.5 min)
1. Log in as manager@goalvault.com
2. Show team dashboard — pending approval count
3. Open pending goal → inline edit target → approve → goal locks
4. Open check-in module → show Planned vs. Actual table
5. Click "Generate AI Summary" → AI writes check-in comment
6. Edit and submit comment

### Role 3 — Admin (3 min)
1. Log in as admin@goalvault.com
2. Show completion dashboard — real-time check-in rates
3. Show cycle config — explain windows
4. Navigate to Audit Trail
5. **DEMO MOMENT:** Click "Verify Chain Integrity" → green banner "Chain Intact ✓"
6. Open DB tool in another window → manually modify one audit log row
7. Re-click "Verify Chain Integrity" → red banner with broken entry highlighted
8. Explain: "This is a tamper-evident audit trail — no other team has this"
9. Show achievement report → Export to Excel → download

---

## 12. Architecture Diagram Description

Draw this in Excalidraw (excalidraw.com) or draw.io:

```
[Browser Layer]
  Bootstrap 5 UI ←→ Jinja2 Templates ←→ Vanilla JS (AJAX)

[Application Layer - Flask]
  /auth/* ←→ /employee/* ←→ /manager/* ←→ /admin/* ←→ /api/*
       ↓             ↓              ↓              ↓
  [Service Layer]
  GoalService | AuditService | AIService | ExportService | EscalationService

[Data Layer]
  SQLAlchemy ORM → SQLite (dev) / PostgreSQL (prod)

[External Services]
  Groq API (llama-3.1-70b) ← AIService
  APScheduler ← EscalationService (daily job)

[Security Layer - Horizontal]
  Flask-WTF (CSRF) | Flask-Limiter (Rate Limit) | 
  Hash-Chain Audit | Role Decorators | Security Headers
```

---

## 13. Setup & Run Instructions

### Local Development

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/goalvault
cd goalvault
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env:
#   SECRET_KEY=your-random-secret-key
#   GROQ_API_KEY=your-groq-api-key
#   DATABASE_URL=sqlite:///goalvault.db
#   FLASK_ENV=development

# 4. Initialize database
flask db upgrade

# 5. Seed demo data
python seed_data.py

# 6. Run
flask run
# Open http://localhost:5000
```

### Demo Credentials (post-seed)

| Role | Email | Password |
|---|---|---|
| Admin | admin@goalvault.com | Admin@123 |
| Manager | manager@goalvault.com | Manager@123 |
| Employee | employee@goalvault.com | Employee@123 |

### Production Deployment (Railway)

```bash
# 1. Install Railway CLI: npm i -g @railway/cli
# 2. railway login
# 3. railway init
# 4. Add PostgreSQL plugin in Railway dashboard
# 5. Set environment variables in Railway dashboard
# 6. railway up
# 7. railway run flask db upgrade
# 8. railway run python seed_data.py
```

### requirements.txt

```
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
flask-login>=0.6.3
flask-wtf>=1.2.1
flask-limiter>=3.5.0
flask-cors>=4.0.0
apscheduler>=3.10.4
pandas>=2.1.0
openpyxl>=3.1.2
requests>=2.31.0
python-dotenv>=1.0.0
bleach>=6.1.0
gunicorn>=21.2.0
werkzeug>=3.0.0
wtforms>=3.1.0
```

---

## Summary Scorecard (Evaluation Criteria Mapping)

| Evaluation Criterion | What You're Delivering | Confidence |
|---|---|---|
| Functionality of the Portal | All Phase 1 + 2 features, all 3 role journeys | ✅ High |
| Adherence to BRD | All validation rules implemented, all must-haves covered | ✅ High |
| User Friendliness | Bootstrap 5, real-time feedback, helpful errors | ✅ High |
| Presence of Bugs | Seed data, tested demo script, edge case validators | ✅ Medium-High |
| Good-to-Have Features | Analytics dashboard + Escalation module | ✅ Medium |
| Cost Optimisation | SQLite → PG, Groq free tier, no unnecessary APIs | ✅ High |
| **Differentiator** | **Hash-chain audit + AI Goal Coach** | 🔥 Unique |
```
