import os
from flask import Flask, jsonify, send_from_directory, g
from flask_cors import CORS

from .database import Base, engine, SessionLocal
from .seed import seed_database
from .auth import APIError
from .routers import (
    auth_router,
    faculty_router,
    timetable_router,
    rooms_router,
    substitutes_router,
    analytics_router,
    api_router
)

# Root directory containing frontend assets (index.html, admin.html, etc.)
FRONTEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_app(test_config=None) -> Flask:
    app = Flask(__name__)

    # Default configuration
    secret_key = (
        os.getenv("EDUNOVA_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or "edunova-secure-jwt-secret-key-2026"
    )
    app.config["SECRET_KEY"] = secret_key

    if test_config:
        app.config.update(test_config)

    # Enable Cross-Origin Resource Sharing
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"]
    )

    # Ensure database schema is present
    Base.metadata.create_all(bind=engine)

    # Seed initial database if empty / ensure AI&DS classes & timetables
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # Automatically close database sessions on request teardown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db = getattr(g, "db", None)
        if db is not None:
            db.close()
            g.db = None

    # Standardized API error handling
    @app.errorhandler(APIError)
    def handle_api_error(err):
        return jsonify({"detail": err.detail}), err.status_code

    # Register Blueprints
    app.register_blueprint(api_router)
    app.register_blueprint(auth_router)
    app.register_blueprint(faculty_router)
    app.register_blueprint(timetable_router)
    app.register_blueprint(rooms_router)
    app.register_blueprint(substitutes_router)
    app.register_blueprint(analytics_router)

    # Health Checks (both /health and /api/health)
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # Root route: Serves index.html
    @app.route("/", methods=["GET"])
    def root():
        root_index = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(root_index):
            return send_from_directory(FRONTEND_DIR, "index.html")
        return "<h1>EduNova Backend is running</h1><p>Flask Smart Timetable Manager</p>", 200

    # Dedicated clean routes for core frontend pages
    @app.route("/login", methods=["GET"])
    def login_page():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/admin", methods=["GET"])
    def admin_page():
        return send_from_directory(FRONTEND_DIR, "admin.html")

    @app.route("/faculty", methods=["GET"])
    def faculty_page():
        return send_from_directory(FRONTEND_DIR, "faculty.html")

    # Frontend Static Files: Serves admin.html, faculty.html, timetable-data.js, etc.
    @app.route("/<path:filename>", methods=["GET"])
    def static_frontend_files(filename):
        target_path = os.path.join(FRONTEND_DIR, filename)
        if os.path.exists(target_path) and os.path.isfile(target_path):
            return send_from_directory(FRONTEND_DIR, filename)
        # Support clean URLs without .html extension (e.g. /admin -> admin.html)
        html_candidate = target_path + ".html"
        if os.path.exists(html_candidate) and os.path.isfile(html_candidate):
            return send_from_directory(FRONTEND_DIR, filename + ".html")
        return jsonify({"detail": f"File '{filename}' not found"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
