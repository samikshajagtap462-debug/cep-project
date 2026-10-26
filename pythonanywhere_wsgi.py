# ==============================================================================
# PythonAnywhere WSGI Configuration for EduNova Smart Timetable Manager
# ==============================================================================
# Instructions:
# 1. In your PythonAnywhere Dashboard, go to the "Web" tab.
# 2. Click the link under "Code:" -> "WSGI configuration file:"
#    (e.g., /var/www/yourusername_pythonanywhere_com_wsgi.py)
# 3. Replace the entire contents of that file with this configuration.
# 4. Replace 'YOUR_USERNAME' below with your actual PythonAnywhere username.
# ==============================================================================

import os
import sys

# Replace this with your actual PythonAnywhere username (in lowercase)
USERNAME = "YOUR_USERNAME"

# Define project directories in your PythonAnywhere home directory
PROJECT_ROOT = f"/home/{USERNAME}/cep-project"
APP_SUBDIR = os.path.join(PROJECT_ROOT, "smart-timetable-manager-main")

# Add directories to Python's module search path
for directory in [PROJECT_ROOT, APP_SUBDIR]:
    if directory not in sys.path:
        sys.path.insert(0, directory)

# Production Environment Variables
os.environ["FLASK_DEBUG"] = "false"
os.environ["EDUNOVA_SECRET_KEY"] = "edunova-secure-jwt-production-secret-2026"

# Configure the SQLite database to live in your persistent home directory:
# When you upload your edunova.db into smart-timetable-manager-main/backend/,
# this path ensures all reads and writes are 100% persistent!
os.environ["DATABASE_PATH"] = os.path.join(APP_SUBDIR, "backend", "edunova.db")

# Import the Flask application callable as 'application' (expected by PythonAnywhere)
from app import app as application  # noqa: E402
