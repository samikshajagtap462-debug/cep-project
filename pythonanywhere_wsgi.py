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

# 1. Project Directory Paths
USERNAME = "samjjj"
PROJECT_ROOT = f"/home/{USERNAME}/cep-project"
APP_SUBDIR = os.path.join(PROJECT_ROOT, "smart-timetable-manager-main")

# 2. Add directories to Python sys.path
for directory in [PROJECT_ROOT, APP_SUBDIR]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

# 3. Production Environment Configuration
os.environ["FLASK_DEBUG"] = "false"

# Absolute persistent database path in the application's backend directory:
os.environ["DATABASE_PATH"] = os.path.join(APP_SUBDIR, "backend", "edunova.db")

# Production JWT secret key (reads existing env or falls back safely)
if "EDUNOVA_SECRET_KEY" not in os.environ:
    os.environ["EDUNOVA_SECRET_KEY"] = "edunova-jwt-prod-samjjj-2026-sec"

# 4. Import the real Flask application instance as 'application' (WSGI standard)
from backend.app.main import app as application  # noqa: E402
