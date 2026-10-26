# ==============================================================================
# PythonAnywhere WSGI Configuration for EduNova Smart Timetable Manager
# Active Account: samjjj | Domain: samjjj.pythonanywhere.com
# ==============================================================================
# Instructions:
# 1. In PythonAnywhere Web Tab -> click link for "WSGI configuration file:"
#    Path: /var/www/samjjj_pythonanywhere_com_wsgi.py
# 2. Paste this entire file content into that configuration file and click Save.
# ==============================================================================

import os
import sys

# 1. Project Directory Paths for samjjj
PROJECT_ROOT = "/home/samjjj/cep-project"
APP_SUBDIR = os.path.join(PROJECT_ROOT, "smart-timetable-manager-main")

# 2. Add directories to Python sys.path cleanly
for directory in [PROJECT_ROOT, APP_SUBDIR]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

# 3. Production Environment Configuration
os.environ["FLASK_DEBUG"] = "false"

# 4. Resilient Database Path Selection
# Priority 1: Backend directory inside project
backend_db = os.path.join(APP_SUBDIR, "backend", "edunova.db")
# Priority 2: Account home root directory
home_db = "/home/samjjj/edunova.db"

if os.path.exists(backend_db) and os.path.getsize(backend_db) > 0:
    os.environ["DATABASE_PATH"] = backend_db
elif os.path.exists(home_db) and os.path.getsize(home_db) > 0:
    os.environ["DATABASE_PATH"] = home_db
else:
    os.environ["DATABASE_PATH"] = backend_db

# 5. Production JWT secret key
if "EDUNOVA_SECRET_KEY" not in os.environ:
    os.environ["EDUNOVA_SECRET_KEY"] = "edunova-jwt-prod-samjjj-2026-sec"

# 6. Import the real Flask application instance as 'application' (WSGI standard)
from backend.app.main import app as application  # noqa: E402
