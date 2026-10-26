import os
import sys
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import create_app
from backend.app.database import SessionLocal, get_db
from backend.app.models import Faculty


@pytest.fixture(scope="session")
def app():
    app = create_app({"TESTING": True})
    return app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def admin_token(client):
    res = client.post("/auth/login/admin", json={
        "admin_id": "ADM-101",
        "password": "admin123"
    })
    assert res.status_code == 200, f"Admin login failed: {res.data}"
    data = res.get_json()
    return data["access_token"]


@pytest.fixture(scope="session")
def faculty_token(client):
    res = client.post("/auth/login/faculty", json={
        "email": "sharma@edunova.edu",
        "faculty_id": "FAC-101",
        "password": "faculty123"
    })
    assert res.status_code == 200, f"Faculty login failed: {res.data}"
    data = res.get_json()
    return data["access_token"]


@pytest.fixture(scope="session")
def second_faculty_token(client):
    res = client.post("/auth/login/faculty", json={
        "email": "patil@edunova.edu",
        "faculty_id": "FAC-102",
        "password": "faculty123"
    })
    assert res.status_code == 200, f"Second faculty login failed: {res.data}"
    data = res.get_json()
    return data["access_token"]
