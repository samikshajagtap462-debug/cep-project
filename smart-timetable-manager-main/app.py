import os
import sys

# Ensure backend directory is in python module search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    print(f"Starting Smart Timetable Manager Flask Server on port {port} (debug={debug}) ...")
    app.run(host="0.0.0.0", port=port, debug=debug)
