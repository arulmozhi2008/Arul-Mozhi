# FitBuddy – AI Fitness Plan Generator

Complete FastAPI + Jinja2 + SQLite/SQLAlchemy + Gemini implementation based on the supplied project documentation.

## VS Code setup

Install Python 3.11+ and open this folder in VS Code.

### Windows PowerShell
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and put your Gemini API key in `GEMINI_API_KEY`. The model names are configurable environment variables.

## Run
```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs.

SQLite is created automatically as `fitbuddy.db`.

## Test
```bash
pytest
```

Tests do not call Gemini. They verify the home page, admin protection and missing-user API behavior.

## Features

- User form with name, user ID, age, weight, goal, intensity and experience.
- AI-generated structured 7-day workout plan.
- AI nutrition/recovery tip.
- Feedback-based AI plan revision.
- SQLite persistence through SQLAlchemy.
- JSON endpoint `/api/users/{user_id}`.
- Session-protected admin dashboard at `/view-all-users`.
- Responsive Jinja2 frontend.
- Environment-based Gemini/API/admin configuration.

## Important

The original documentation names Gemini 1.5 Pro and Gemini Flash. This implementation keeps the Pro/Flash architecture but makes model names configurable and uses the current `google-genai` Python SDK interface. If a configured model is unavailable for your API account, change the two model environment variables to models currently available to your account.

This is a general wellness application, not medical advice. For production deployment, add stronger authentication, CSRF protection, rate limiting, HTTPS, secret management, database migrations and audit logging.
