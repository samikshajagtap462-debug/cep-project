import os
import shutil
import tempfile
import pytest

from backend.app.database import (
    resolve_database_config,
    BUNDLED_DB_PATH,
    DB_PATH
)
from backend.app.main import create_app


def test_clean_frontend_page_routes(client):
    """Ensure Flask serves login, admin, faculty, and static assets with clean URLs."""
    # Root -> index.html (login page)
    res = client.get("/")
    assert res.status_code == 200
    assert b"EduNova" in res.data or b"login" in res.data.lower()

    # /login -> index.html
    res_login = client.get("/login")
    assert res_login.status_code == 200
    assert b"EduNova" in res_login.data or b"login" in res_login.data.lower()

    # /admin and /admin.html
    res_admin = client.get("/admin")
    assert res_admin.status_code == 200
    assert b"Admin" in res_admin.data or b"timetable" in res_admin.data.lower()

    res_admin_html = client.get("/admin.html")
    assert res_admin_html.status_code == 200

    # /faculty.html
    res_faculty_html = client.get("/faculty.html")
    assert res_faculty_html.status_code == 200
    assert b"Faculty" in res_faculty_html.data or b"timetable" in res_faculty_html.data.lower()

    # /timetable-data.js
    res_js = client.get("/timetable-data.js")
    assert res_js.status_code == 200
    assert b"MASTER_TIMETABLE" in res_js.data or b"EduNova" in res_js.data

    # Non-existent file returns 404
    res_404 = client.get("/does_not_exist_xyz.txt")
    assert res_404.status_code == 404


def test_persistent_database_resolution_default():
    """Default resolution uses bundled edunova.db."""
    url, path = resolve_database_config()
    assert path is not None
    assert os.path.exists(path)
    assert path == BUNDLED_DB_PATH
    assert "sqlite:///" in url


def test_persistent_database_safe_initialization_on_empty_disk(monkeypatch):
    """
    Simulates a newly attached Render persistent disk at /var/data.
    On first boot, the target file does not exist.
    The system must safely copy the bundled database to the target path without corrupting source.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_target = os.path.join(tmpdir, "persistent_disk", "edunova.db")
        assert not os.path.exists(mock_target)

        # Set DATABASE_PATH to mock persistent path
        monkeypatch.setenv("DATABASE_PATH", mock_target)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        url, resolved_path = resolve_database_config()
        assert resolved_path == os.path.abspath(mock_target)
        assert os.path.exists(resolved_path)
        # Size matches original bundled database
        assert os.path.getsize(resolved_path) == os.path.getsize(BUNDLED_DB_PATH)


def test_persistent_database_never_overwrites_existing_disk(monkeypatch):
    """
    Simulates subsequent deploys or restarts on Render where persistent disk already has data.
    The system must NEVER overwrite or reset the existing database.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_target = os.path.join(tmpdir, "persistent_disk", "edunova.db")
        os.makedirs(os.path.dirname(mock_target), exist_ok=True)

        # Write existing user data to target
        sentinel_content = b"CUSTOM_USER_DATA_SENTINEL_2026"
        with open(mock_target, "wb") as f:
            f.write(sentinel_content)

        monkeypatch.setenv("DATABASE_PATH", mock_target)
        monkeypatch.delenv("DATABASE_URL", raising=False)

        url, resolved_path = resolve_database_config()
        assert resolved_path == os.path.abspath(mock_target)
        with open(resolved_path, "rb") as f:
            content = f.read()
        assert content == sentinel_content, "Existing persistent database was overwritten!"


def test_postgres_url_normalization(monkeypatch):
    """Ensure postgres:// is automatically normalized to postgresql:// for SQLAlchemy."""
    monkeypatch.setenv("DATABASE_URL", "postgres://user:password@render.com/edunova")
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    monkeypatch.delenv("SQLITE_DB_PATH", raising=False)

    url, path = resolve_database_config()
    assert url.startswith("postgresql://")
    assert path is None


def test_secret_key_configuration(monkeypatch):
    """Ensure SECRET_KEY environment variable is respected."""
    custom_secret = "super-secret-render-token-key-xyz"
    monkeypatch.setenv("SECRET_KEY", custom_secret)
    monkeypatch.delenv("EDUNOVA_SECRET_KEY", raising=False)

    test_app = create_app()
    assert test_app.config["SECRET_KEY"] == custom_secret


def _resolve_project_file(rel_path):
    for candidate in [
        os.path.abspath(rel_path),
        os.path.abspath(os.path.join("smart-timetable-manager-main", rel_path)),
        os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), rel_path))
    ]:
        if os.path.exists(candidate):
            return candidate
    return os.path.abspath(rel_path)


def test_requirements_and_render_config():
    """Ensure gunicorn and render configuration files exist and are valid."""
    # Check backend requirements
    backend_req = _resolve_project_file("backend/requirements.txt")
    assert os.path.exists(backend_req)
    with open(backend_req, "r") as f:
        assert "gunicorn" in f.read().lower()

    # Check root requirements
    root_req = _resolve_project_file("requirements.txt")
    assert os.path.exists(root_req)
    with open(root_req, "r") as f:
        assert "gunicorn" in f.read().lower()

    # Check render.yaml Blueprint
    render_yaml = _resolve_project_file("render.yaml")
    assert os.path.exists(render_yaml)
    with open(render_yaml, "r") as f:
        render_content = f.read()
        assert "gunicorn" in render_content
        assert "/var/data" in render_content
        assert "app:app" in render_content
