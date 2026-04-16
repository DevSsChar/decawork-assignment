# IT Support AI Agent

AI agent that takes natural-language IT support requests and executes them
on a mock admin panel using browser automation (no DOM shortcuts).

## Architecture
- **Panel**: FastAPI + Jinja2, in-memory state, port 8000
- **Agent**: browser-use + ChatGroq (originally Claude), Playwright/Chromium

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure environment
```bash
cp .env.example .env
# Add your GROQ_API_KEY
```

### 3. Start the admin panel
From the project root directory (`it-support-agent`), make sure your virtual environment is activated, then run:

**Windows:**
```bash
.\deca\Scripts\activate
python -m uvicorn panel.main:app --host 127.0.0.1 --port 8000 --reload
```

**Mac/Linux:**
```bash
source deca/bin/activate
python -m uvicorn panel.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Run a task (new terminal)
```bash
python -m agent.runner "Reset password for alice@company.com"
```

### Run the demo (3 tasks)
```bash
python demo/run_demo.py
```

## Supported Task Types
- Password reset
- Create user
- Suspend / activate user
- Assign / revoke license
- Multi-step conditional (check → create → assign)

## Pre-seeded Users
- alice@company.com (Engineering, active)
- bob@company.com (Sales, active)  
- charlie@company.com (HR, suspended)

---

## 🚀 Progress Track (Work Completed so far)

**Phase 1: Project Scaffolding & Setup (DONE)**
- `requirements.txt` configured with Groq logic.
- `.env.example` and `.gitignore` created.
- `database.py` created with pre-seeded users and logging functionality.
- `main.py` created initializing FastAPI, Jinja2, and SessionMiddleware.

**Phase 2: Panel Templates & UI (DONE)**
- `style.css` implemented exact PRD specs for alert boxes and tables.
- `base.html` constructed with navigation routing.
- `index.html`, `users.html`, `user_detail.html`, `reset_password.html`, and `licenses.html` all generated ensuring exact inputs required for the AI agent to automate.

**Phase 3: Panel Routes & Actions (DONE)**
- `users.py` handles creation, status suspension, and list views.
- `passwords.py` handles the mock `Temp{4-digit}!` resets.
- `licenses.py` handles assigning and revoking logic + checks formatting.

**Phase 4: Agent Core Logic (PENDING)**
- Next step involves generating `agent.py`, `tasks.py`, `runner.py`, and `demo/run_demo.py`.