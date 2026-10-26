import os
import sys

# Ensure both root and the main project directory are in the Python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_SUBDIR = os.path.join(CURRENT_DIR, "smart-timetable-manager-main")

if PROJECT_SUBDIR not in sys.path:
    sys.path.insert(0, PROJECT_SUBDIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import the configured Flask application
from backend.app.main import app  # noqa: E402

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    print(f"Starting EduNova Smart Timetable Manager on port {port} (debug={debug}) ...")
    app.run(host="0.0.0.0", port=port, debug=debug)
