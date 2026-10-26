# Smart Timetable Manager (EduNova) - Flask + SQL Migration

Smart Timetable & Departmental Management System for academic institutions, migrated from FastAPI to **Python + Flask + SQL (SQLAlchemy ORM & SQLite)**.

---

## 1. Overview & Architecture

The application provides:
- **Backend**: Python 3, Flask, Flask-SQLAlchemy / SQLAlchemy 2.0 ORM, Flask-CORS, PyJWT, Werkzeug/PBKDF2 security hashing.
- **Database**: SQLite SQL engine (`edunova.db`), fully idempotent initialization, safe migrations, and preserved record persistence.
- **Frontend**: Clean and responsive HTML5, TailwindCSS, and JavaScript web interfaces for Administrator/HOD and Faculty users.
- **Department Specifications**: Configured specifically for the **Artificial Intelligence and Data Science (AI&DS)** department.
- **Class Structure (7 Unique Classes)**:
  - **SY (Second Year)**: `SY-AD1`, `SY-AD2`, `SY-AD3`
  - **TY (Third Year)**: `TY-AD1`, `TY-AD2`
  - **BE (Final Year)**: `BE-AD1`, `BE-AD2`

---

## 2. Default Credentials & Role Access

| Account Role | Identifier / Email | Faculty ID / Code | Password | Default Portal |
|---|---|---|---|---|
| **Admin / HOD** | `admin@edunova.edu` or `ADM-101` | `ADM-101` | `admin123` | `admin.html` |
| **Faculty (Dr. Sharma)** | `sharma@edunova.edu` | `FAC-101` | `faculty123` | `faculty.html` |
| **Faculty (Prof. Patil)** | `patil@edunova.edu` | `FAC-102` | `faculty123` | `faculty.html` |
| **Faculty (Prof. Joshi)** | `joshi@edunova.edu` | `FAC-103` | `faculty123` | `faculty.html` |
| **Faculty (Dr. Kulkarni)** | `kulkarni@edunova.edu` | `FAC-104` | `faculty123` | `faculty.html` |
| **Faculty (Prof. Pawar)** | `pawar@edunova.edu` | `FAC-105` | `faculty123` | `faculty.html` |

---

## 3. Installation & Setup (Windows PowerShell)

### Step 1: Open PowerShell and Navigate to the Repository
```powershell
cd smart-timetable-manager-main
```

### Step 2: Install Backend Dependencies
Install the required Flask and SQLAlchemy packages:
```powershell
pip install -r backend/requirements.txt
```

*(Optional)* If you wish to configure environment variables:
```powershell
Copy-Item .env.example .env
```

---

## 4. Starting the Application

You can start the Flask backend using any of the following standard commands in PowerShell:

### Option A: Using the Root Entrypoint (Recommended)
```powershell
python app.py
```

### Option B: Using the Backend Module
```powershell
python -m backend.app.main
```

### Option C: Using Flask CLI
```powershell
$env:FLASK_APP = "app.py"
flask run --host=127.0.0.1 --port=5000
```

Once started, open your web browser:
- **Landing & Login Interface**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Admin Dashboard**: [http://127.0.0.1:5000/admin.html](http://127.0.0.1:5000/admin.html)
- **Faculty Portal**: [http://127.0.0.1:5000/faculty.html](http://127.0.0.1:5000/faculty.html)
- **Backend Health Check**: [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)

---

## 5. Running Automated Tests

Run the full pytest test suite (25 automated tests verifying startup, authentication, database persistence, role-based privacy, timetable clash detection, room occupancy, substitution lifecycle, and all 7 AI&DS classes):

```powershell
python -m pytest tests -v
```

---

## 6. API Reference (Flask Blueprints)

### Authentication (`/auth`)
- `POST /auth/login/faculty` — Authenticates faculty (requires `email`, `faculty_id`, `password`)
- `POST /auth/login/admin` — Authenticates Administrator / HOD (requires `admin_id`, `password`)
- `POST /auth/login` — Generic fallback login
- `GET /auth/me` — Retrieves current user profile from JWT Bearer token

### Faculty Management (`/faculty`)
- `GET /faculty` — Lists faculty (privacy-scoped for faculty; full directory for admin)
- `GET /faculty/<id>` — Retrieves single faculty details (privacy protected)
- `POST /faculty` — Creates new faculty member (Admin only)
- `PUT /faculty/<id>` — Updates faculty details (Admin only)
- `DELETE /faculty/<id>` — Deactivates faculty member (Admin only)

### Timetable (`/timetable`)
- `GET /timetable` — Queries timetable entries (filters: `day`, `class_name`, `faculty_id`, `search`)
- `GET /timetable/<id>` — Retrieves single timetable entry
- `POST /timetable` — Creates timetable entry with clash verification for faculty, room, and class (Admin only)
- `DELETE /timetable/<id>` — Deletes timetable entry (Admin only)
- `GET /timetable/clashes/check` — Audits the master timetable and reports any schedule clashes

### Rooms & Occupancy (`/rooms`)
- `GET /rooms/occupancy` — Reports room availability and occupancy for a given day and slot

### Substitutes (`/substitutes`)
- `GET /substitutes/recommend` — AI substitute recommendation based on department, availability, and workload
- `GET /substitutes/availability` — Checks faculty availability for a day and time slot
- `POST /substitutes/request` — Submits a peer lecture substitution request
- `PUT /substitutes/request/<id>` — Accepts or rejects a substitute request

---

## 7. Render Production Deployment Guide

EduNova is production-ready for deployment on [Render](https://render.com).

### Deployment Architecture & Specifications:
- **Web Service Type**: Python Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
- **WSGI Entrypoint**: `app:app` (defined in `app.py`)
- **Port Handling**: Uses Render's dynamic `$PORT` environment variable.

### Persistent SQLite Database on Render:
1. When creating your Web Service on Render, attach a **Persistent Disk**:
   - **Disk Name**: `edunova-data`
   - **Mount Path**: `/var/data`
   - **Size**: 1 GB (or larger)
2. In the Render Dashboard **Environment Variables**, configure:
   - `DATABASE_PATH`: `/var/data/edunova.db`
   - `EDUNOVA_SECRET_KEY`: (Click "Generate" to generate a secure random secret key)
   - `FLASK_DEBUG`: `false`
   - `PYTHON_VERSION`: `3.11.9`
3. **Safe One-Time Database Initialization**:
   - On the very first deployment with an empty persistent disk, EduNova auto-detects that `/var/data/edunova.db` does not exist and safely copies the bundled SQLite database (`backend/edunova.db`) with all existing faculty, AI&DS classes, rooms, and timetables onto the disk.
   - On all subsequent deployments, container restarts, or Git code updates, the application verifies the database already exists on `/var/data` and **NEVER overwrites it**. All new faculty records, timetable changes, and substitution records are preserved permanently.
4. **Deploying with Blueprint (`render.yaml`)**:
   - A pre-configured `render.yaml` file is included in the project root. If you deploy using Render Blueprints ("New Blueprint Instance"), Render will automatically provision the Python Web Service, attach the `/var/data` persistent disk, set the start command, and configure environment variables.

### Deploying via Private GitHub Repository:
1. Keep your GitHub repository **Private** to ensure your project data and credentials remain secure.
2. Initialize and push your repository:
   ```bash
   git init
   git add .
   git commit -m "EduNova production deployment setup"
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
3. In Render, select **New > Web Service**, connect your private GitHub repository, and deploy!
