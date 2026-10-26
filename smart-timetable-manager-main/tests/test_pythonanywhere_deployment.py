import os
import sys
import tempfile
import pytest

# Ensure root and smart-timetable-manager-main are in search path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for d in [ROOT_DIR, APP_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.app.database import resolve_database_config, BUNDLED_DB_PATH
from backend.app.main import create_app


def test_pythonanywhere_wsgi_callable_and_routes():
    """Ensure standard WSGI 'application' callable works for PythonAnywhere."""
    from app import app as application
    assert application is not None

    client = application.test_client()

    # Core page routes
    res_root = client.get("/")
    assert res_root.status_code == 200

    res_admin = client.get("/admin.html")
    assert res_admin.status_code == 200

    res_faculty = client.get("/faculty.html")
    assert res_faculty.status_code == 200

    # API health check
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json.get("status") == "ok"


def test_pythonanywhere_persistent_home_directory_path(monkeypatch):
    """
    Simulates PythonAnywhere environment where database is stored in a writable home directory
    such as /home/username/edunova.db (or inside the cloned repo directory).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_pa_home_db = os.path.join(tmpdir, "home", "username", "edunova.db")
        os.makedirs(os.path.dirname(mock_pa_home_db), exist_ok=True)

        sentinel_bytes = b"PYTHONANYWHERE_PERSISTENT_SQLITE_2026"
        with open(mock_pa_home_db, "wb") as f:
            f.write(sentinel_bytes)

        # Set environment variable as configured in PythonAnywhere WSGI file
        monkeypatch.setenv("DATABASE_PATH", mock_pa_home_db)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        url, resolved_path = resolve_database_config()
        assert resolved_path == os.path.abspath(mock_pa_home_db)
        assert os.path.exists(resolved_path)

        with open(resolved_path, "rb") as f:
            assert f.read() == sentinel_bytes, "PythonAnywhere persistent database was modified!"


def test_pythonanywhere_default_fallback_without_render(monkeypatch):
    """
    On PythonAnywhere, /var/data does not exist.
    If no DATABASE_PATH is provided, it falls back to the bundled project database path.
    """
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("SQLITE_DB_PATH", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    url, resolved_path = resolve_database_config()
    assert resolved_path == BUNDLED_DB_PATH
    assert "sqlite:///" in url
