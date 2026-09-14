# Pothole AI — Backend & Database Module (Anika's Part)

**Role:** Backend & DB Lead
**Ownership share:** 16.67%
**Tech:** Python · Flask · SQLAlchemy · SQLite/MySQL · JWT Auth · Pandas · ReportLab

This backend is set up to run locally with SQLite by default, which avoids the MySQL connection problem on machines without a database server installed.

## 1) Prerequisites

- Python 3.10+ (Python 3.12 was verified on this Windows machine)
- PowerShell on Windows, or Bash/Zsh on macOS/Linux
- Optional: GNU Make if you want to use the Makefile commands

## 2) Recommended setup for Windows

From the project root:

```powershell
cd "C:\Users\SATVIK\Downloads\POTHOLE-AI-Anika-Backend\POTHOLE-AI"
py -3.12 -m venv backend.venv
.\backend.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\backend\requirements.txt
Copy-Item .\backend\.env.example .\backend\.env
```

Then open the file:

```text
backend/.env
```

and make sure it contains:

```env
USE_SQLITE=True
```

If you do not want to use SQLite, you can switch back to MySQL later by setting the `DB_*` variables instead.

## 3) Initialize the database

```powershell
cd backend
python database/init_db.py
```

Optional demo data:

```powershell
python database/seed_data.py
```

## 4) Start the backend

```powershell
cd backend
python run.py
```

The app will run at:

```text
http://localhost:5000
```

## 5) Health check

Open this URL in a browser or terminal:

```text
http://localhost:5000/api/health
```

Expected response:

```json
{"status": "ok", "service": "pothole-ai-backend"}
```

## 6) If GNU Make is installed

If you have `make` available, this project also supports the following commands from the repo root:

```bash
make install
make env
make db
make run
make test
make health
```

If `make` is not installed on your machine, use the PowerShell commands above instead.

## 7) API quick reference

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create user |
| POST | `/api/auth/login` | No | Login and get JWT |
| GET | `/api/auth/me` | Yes | Current user info |
| POST | `/api/upload/image` | Yes | Upload image |
| POST | `/api/upload/video` | Yes | Upload video |
| POST | `/api/detect/<detection_id>` | Yes | Run detection |
| GET | `/api/detect/<detection_id>` | Yes | Fetch result |
| GET | `/api/history` | Yes | View detection history |
| DELETE | `/api/history/<detection_id>` | Yes | Delete record |
| GET | `/api/report/csv` | Yes | Export CSV |
| GET | `/api/report/pdf` | Yes | Export PDF |
| GET | `/api/health` | No | Health check |

## 8) Testing

```powershell
cd backend
pytest -q
```

## 9) Common issues

### `make: command not found`

This means GNU Make is not installed on your machine. Use the PowerShell commands above instead.

### MySQL connection refused

This usually means the app is still pointed at MySQL instead of SQLite. Make sure your `.env` contains:

```env
USE_SQLITE=True
```

### Missing Flask modules

Reinstall the dependencies:

```powershell
python -m pip install -r .\backend\requirements.txt
```

## 10) Production note

For deployment, use a WSGI server such as Gunicorn:

```bash
gunicorn run:app --bind 0.0.0.0:5000
```

This repository already includes `gunicorn` in the backend requirements for deployment use.

For deployment, the app is structured to work with a WSGI server such as Gunicorn:

```bash
gunicorn run:app --bind 0.0.0.0:5000
```

## 11) Notes for the team

This backend is prepared so other teammates can plug in their modules without changing the API contract:

- AI/Model Lead: replace the mock detection logic in `backend/utils/mock_detector.py`
- Frontend team: use the `/api/*` routes directly
- Maps team: read the `latitude`, `longitude`, and `severity` fields from history records

For more detailed request/response examples, see:

```text
docs/ANIKA_BACKEND_DOCUMENTATION.md
```
