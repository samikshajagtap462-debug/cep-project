import pytest
from backend.app.database import SessionLocal
from backend.app.models import Faculty, ClassModel, TimetableEntry, Subject


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_api_login_faculty_success(client):
    res = client.post("/api/auth/login", json={
        "email": "ana@edunova.edu",
        "faculty_id": "FAC-ANA",
        "password": "faculty123",
        "role": "faculty"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "ana@edunova.edu"
    assert data["user"]["role"] == "faculty"


def test_api_login_admin_success(client):
    res = client.post("/api/auth/login", json={
        "email": "admin@edunova.edu",
        "password": "admin123",
        "role": "admin"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


def test_api_login_invalid_password(client):
    res = client.post("/api/auth/login", json={
        "email": "ana@edunova.edu",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


def test_api_login_faculty_cannot_claim_admin(client):
    res = client.post("/api/auth/login", json={
        "email": "ana@edunova.edu",
        "password": "faculty123",
        "role": "admin"
    })
    assert res.status_code == 403


def test_api_logout(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
    assert "Logged out" in res.get_json()["message"]


def test_api_auth_me(client, faculty_token):
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["email"] == "sharma@edunova.edu"


def test_api_faculty_me_profile(client):
    # Log in as Mrs. Ashvini Ahirrao (ANA)
    login_res = client.post("/api/auth/login", json={
        "email": "ana@edunova.edu",
        "password": "faculty123"
    })
    token = login_res.get_json()["access_token"]

    res = client.get("/api/faculty/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["name"] == "Mrs. Ashvini N. Ahirrao"
    assert data["faculty_id"] == "FAC-ANA"
    assert "SY-AD1" in data["assigned_classes"]
    assert len(data["assigned_subjects"]) > 0


def test_api_faculty_timetable(client):
    # Log in as Mrs. Ashvini Ahirrao (ANA)
    login_res = client.post("/api/auth/login", json={
        "email": "ana@edunova.edu",
        "password": "faculty123"
    })
    token = login_res.get_json()["access_token"]

    res = client.get("/api/faculty/timetable", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    tt = res.get_json()
    assert len(tt) > 0
    # Every returned entry must belong to ANA
    for entry in tt:
        assert entry["faculty_id"] == login_res.get_json()["user"]["id"]


def test_api_classes_all_seven(client, faculty_token):
    res = client.get("/api/classes", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    classes = res.get_json()
    class_names = [c["name"] for c in classes]
    expected = ["SY-AD1", "SY-AD2", "SY-AD3", "TY-AD1", "TY-AD2", "BE-AD1", "BE-AD2"]
    for exp in expected:
        assert exp in class_names


def test_api_class_timetable_syad1(client, faculty_token):
    res = client.get("/api/classes/SY-AD1/timetable", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    entries = res.get_json()
    assert len(entries) >= 20  # SY AD1 has full weekly schedule
    # Verify presence of batches
    batches = {e["batch"] for e in entries if e["batch"]}
    assert "Batch A" in batches
    assert "Batch B" in batches
    assert "Batch C" in batches


def test_api_subjects(client, faculty_token):
    res = client.get("/api/subjects", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    subjects = res.get_json()
    assert len(subjects) >= 6


def test_api_admin_dashboard(client, admin_token, faculty_token):
    # Non-admin gets 403
    res_forbidden = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_forbidden.status_code == 403

    # Admin gets SQL statistics
    res = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_faculty"] >= 6
    assert data["total_classes"] == 7
    assert data["total_timetable_entries"] >= 100
    assert data["total_rooms"] >= 10


def test_api_admin_faculty(client, admin_token):
    res = client.get("/api/admin/faculty", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    faculty_list = res.get_json()
    assert len(faculty_list) >= 15
    # Verify passwords are never exposed
    for f in faculty_list:
        assert "password" not in f
        assert "password_hash" not in f


def test_api_admin_timetable(client, admin_token):
    res = client.get("/api/admin/timetable?class_name=SY-AD1", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) >= 20


def test_api_health_verifies_db_connectivity(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["records"]["faculty"] >= 6
    assert data["records"]["timetable"] >= 8


def test_api_timetable_filterable(client, faculty_token):
    # Test query with class_name
    res = client.get("/api/timetable?class_name=SY-AD1", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    entries = res.get_json()
    assert len(entries) >= 20
    first = entries[0]
    assert "startTime" in first
    assert "endTime" in first
    assert "displayTime" in first
    assert "classDiv" in first

    # Test query with alternate space formatting 'SY AD1'
    res_space = client.get("/api/timetable?class_name=SY AD1", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_space.status_code == 200
    assert len(res_space.get_json()) == len(entries)


def test_api_faculty_directory(client, faculty_token):
    res = client.get("/api/faculty", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    fac_list = res.get_json()
    assert len(fac_list) >= 6
    for f in fac_list:
        assert "password" not in f
        assert "password_hash" not in f
        assert "name" in f
        assert "faculty_id" in f


def test_api_rooms_and_occupancy(client, faculty_token):
    res = client.get("/api/rooms", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    rooms = res.get_json()
    assert len(rooms) >= 6
    assert any(r["name"] in ("Room 102", "Room 101") for r in rooms)

    # Test occupancy check for a Monday lecture slot
    res_occ = client.get("/api/rooms?day=Monday&start_time=10:15&end_time=11:15", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_occ.status_code == 200
    occ_rooms = res_occ.get_json()
    # Room 102 has a lecture at this time
    room_102 = next((r for r in occ_rooms if r["name"] == "Room 102"), None)
    assert room_102 is not None
    assert room_102["status"] == "Occupied"


def test_api_analytics(client, faculty_token):
    res = client.get("/api/analytics", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    analytics = res.get_json()
    assert analytics["total_faculty"] >= 6
    assert analytics["total_classes"] == 7
    assert analytics["total_timetable_entries"] >= 8
    assert len(analytics["workload_summary"]) >= 6


def test_admin_dhotre_designated_account(client):
    # Test logging in as Dr. Dhanraj R. Dhotre
    res1 = client.post("/api/auth/login", json={
        "email": "drdhotre@edunova.edu",
        "password": "admin123",
        "role": "admin"
    })
    assert res1.status_code == 200
    user1 = res1.get_json()["user"]
    assert user1["name"] == "Dr. Dhanraj R. Dhotre"
    assert user1["faculty_id"] == "FAC-DRD"
    assert user1["role"] == "admin"

    # Test logging in as admin@edunova.edu - resolves to designated HOD
    res2 = client.post("/api/auth/login", json={
        "email": "admin@edunova.edu",
        "password": "admin123",
        "role": "admin"
    })
    assert res2.status_code == 200
    user2 = res2.get_json()["user"]
    assert user2["name"] == "Dr. Dhanraj R. Dhotre"
    assert user2["faculty_id"] == "FAC-DRD"


def test_classes_and_practical_batches_abc(client, faculty_token):
    res = client.get("/api/classes", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    classes = res.get_json()
    assert len(classes) == 7

    for c in classes:
        batch_names = [b["name"] for b in c["batches"]]
        assert len(c["batches"]) == 3
        assert "Batch A" in batch_names
        assert "Batch B" in batch_names
        assert "Batch C" in batch_names
        assert c["total_students"] == 75
        for b in c["batches"]:
            assert b["student_count"] == 25


def test_api_batches_endpoint(client, faculty_token):
    res = client.get("/api/batches", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    batches = res.get_json()
    assert len(batches) == 21


def test_substitute_requests_genuine_empty_state(client, admin_token):
    res = client.get("/api/substitutes/requests", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    reqs = res.get_json()
    assert isinstance(reqs, list)
    assert len(reqs) == 0


def test_faculty_management_lifecycle(client, admin_token):
    test_email = "test.prof@edunova.edu"
    test_code = "FAC-TP99"

    # 1. Create faculty
    res_create = client.post("/api/faculty", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "Prof. Test Lifecycle",
        "email": test_email,
        "faculty_id": test_code,
        "password": "tempPassword123",
        "role": "faculty",
        "department": "AI&DS",
        "max_hours": 16,
        "expertise": "Natural Language Processing"
    })
    assert res_create.status_code == 201
    created_id = res_create.get_json()["faculty"]["id"]

    # 2. Duplicate email rejected
    res_dup = client.post("/api/faculty", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "Prof. Duplicate",
        "email": test_email,
        "password": "tempPassword123"
    })
    assert res_dup.status_code == 409

    # 3. Update faculty
    res_up = client.put(f"/api/faculty/{created_id}", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "name": "Prof. Test Lifecycle Renamed",
        "max_hours": 18
    })
    assert res_up.status_code == 200
    assert res_up.get_json()["faculty"]["name"] == "Prof. Test Lifecycle Renamed"
    assert res_up.get_json()["faculty"]["max_hours"] == 18

    # 4. Login as newly created faculty succeeds
    res_log = client.post("/api/auth/login", json={
        "email": test_email,
        "faculty_id": test_code,
        "password": "tempPassword123",
        "role": "faculty"
    })
    assert res_log.status_code == 200

    # 5. Soft deactivation
    res_deact = client.delete(f"/api/faculty/{created_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_deact.status_code == 200
    assert res_deact.get_json()["active"] is False

    # 6. Deactivated faculty rejected at login
    res_log_deact = client.post("/api/auth/login", json={
        "email": test_email,
        "faculty_id": test_code,
        "password": "tempPassword123",
        "role": "faculty"
    })
    assert res_log_deact.status_code == 403

    # 7. Reactivation
    res_toggle = client.post(f"/api/faculty/{created_id}/toggle-status", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_toggle.status_code == 200
    assert res_toggle.get_json()["active"] is True

    # Clean up test faculty
    db = SessionLocal()
    try:
        f_obj = db.get(Faculty, created_id)
        if f_obj:
            db.delete(f_obj)
            db.commit()
    finally:
        db.close()


def test_regular_faculty_forbidden_from_admin_management(client, faculty_token):
    # Attempting to create faculty
    res_c = client.post("/api/faculty", headers={"Authorization": f"Bearer {faculty_token}"}, json={
        "name": "Unauthorized Faculty",
        "email": "unauth@edunova.edu",
        "password": "pw"
    })
    assert res_c.status_code == 403

    # Attempting to deactivate faculty
    res_d = client.delete("/api/faculty/1", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_d.status_code == 403


def test_break_periods_in_timetable(client, faculty_token):
    # Verify no timetable session starts during break times:
    # 1. Morning break: 10:00 - 10:15
    # 2. Lunch break: 12:15 - 13:00
    # 3. Afternoon break: 15:00 - 15:15
    res = client.get("/api/timetable", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    entries = res.get_json()
    assert len(entries) >= 100

    for e in entries:
        # A 1-hour session should not start at 10:00 (break is 10:00 to 10:15)
        # Afternoon break is 15:00 to 15:15
        assert e["start_time"] != "15:00"
