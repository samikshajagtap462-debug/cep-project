import pytest
from backend.app.database import SessionLocal
from backend.app.models import Faculty, TimetableEntry, Subject, Room, SubstituteRequest


# ============================================================================
# 1. APPLICATION STARTUP & FRONTEND STATIC SERVING
# ============================================================================

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_root_serves_index(client):
    res = client.get("/")
    assert res.status_code == 200
    # Must contain HTML content from index.html
    assert b"EduNova" in res.data or b"html" in res.data.lower()


def test_static_frontend_files(client):
    for filename in ["admin.html", "faculty.html", "timetable-data.js"]:
        res = client.get(f"/{filename}")
        assert res.status_code == 200, f"Failed to serve {filename}"
        assert len(res.data) > 0


# ============================================================================
# 2. DATABASE PERSISTENCE & ALL 7 AI&DS CLASSES
# ============================================================================

def test_database_persistence_and_relationships(app):
    with app.app_context():
        db = SessionLocal()
        try:
            faculty_count = db.query(Faculty).count()
            assert faculty_count >= 6, f"Expected at least 6 faculty, got {faculty_count}"

            room_count = db.query(Room).count()
            assert room_count >= 6, f"Expected at least 6 rooms, got {room_count}"

            timetable_count = db.query(TimetableEntry).count()
            assert timetable_count >= 8, f"Expected at least 8 timetable entries, got {timetable_count}"

            subject_count = db.query(Subject).count()
            assert subject_count >= 6, f"Expected at least 6 subjects, got {subject_count}"

            # Verify relationship navigation: entry.faculty
            first_entry = db.query(TimetableEntry).first()
            assert first_entry.faculty is not None
            assert len(first_entry.faculty.name) > 0
        finally:
            db.close()


def test_all_seven_aids_classes(app):
    expected_classes = {
        "SY-AD1",
        "SY-AD2",
        "SY-AD3",
        "TY-AD1",
        "TY-AD2",
        "BE-AD1",
        "BE-AD2"
    }
    with app.app_context():
        db = SessionLocal()
        try:
            classes_in_db = {
                entry.class_name
                for entry in db.query(TimetableEntry).all()
            }
            for cls in expected_classes:
                assert cls in classes_in_db, f"Missing required AI&DS class: {cls}"
        finally:
            db.close()


# ============================================================================
# 3. AUTHENTICATION & JWT VERIFICATION
# ============================================================================

def test_faculty_login_success(client):
    res = client.post("/auth/login/faculty", json={
        "email": "sharma@edunova.edu",
        "faculty_id": "FAC-101",
        "password": "faculty123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "faculty"
    assert data["user"]["department"] == "AI&DS"


def test_faculty_login_invalid_password(client):
    res = client.post("/auth/login/faculty", json={
        "email": "sharma@edunova.edu",
        "faculty_id": "FAC-101",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


def test_faculty_login_mismatched_id(client):
    res = client.post("/auth/login/faculty", json={
        "email": "sharma@edunova.edu",
        "faculty_id": "FAC-999",
        "password": "faculty123"
    })
    assert res.status_code == 401


def test_admin_login_success(client):
    res = client.post("/auth/login/admin", json={
        "admin_id": "ADM-101",
        "password": "admin123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


def test_faculty_cannot_access_admin_login(client):
    res = client.post("/auth/login/admin", json={
        "admin_id": "FAC-101",
        "password": "faculty123"
    })
    assert res.status_code == 403


def test_generic_login(client):
    res = client.post("/auth/login", json={
        "email": "admin@edunova.edu",
        "password": "admin123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["user"]["role"] == "admin"


def test_auth_me_valid_and_invalid(client, faculty_token):
    # Valid
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["email"] == "sharma@edunova.edu"

    # Missing token
    res_no_token = client.get("/auth/me")
    assert res_no_token.status_code == 401

    # Malformed token
    res_bad_token = client.get("/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert res_bad_token.status_code == 401


# ============================================================================
# 4. ROLE-BASED ACCESS CONTROL & PRIVACY
# ============================================================================

def test_faculty_privacy_on_directory(client, faculty_token, admin_token):
    # Faculty sees ONLY themselves
    res_faculty = client.get("/faculty", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_faculty.status_code == 200
    faculty_list = res_faculty.get_json()
    assert len(faculty_list) == 1
    assert faculty_list[0]["email"] == "sharma@edunova.edu"

    # Admin sees ALL active faculty
    res_admin = client.get("/faculty", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    admin_list = res_admin.get_json()
    assert len(admin_list) >= 6


def test_faculty_privacy_single_member(client, faculty_token, second_faculty_token):
    # Dr. Sharma (id=2) accessing Dr. Sharma's record -> OK
    res_self = client.get("/faculty/2", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_self.status_code == 200

    # Dr. Sharma accessing Prof. Patil's record (id=3) -> 403 Forbidden
    res_other = client.get("/faculty/3", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_other.status_code == 403


# ============================================================================
# 5. FACULTY CRUD (ADMIN ONLY)
# ============================================================================

def test_faculty_crud_lifecycle(client, admin_token, faculty_token):
    # 1. Non-admin cannot create
    res_forbidden = client.post("/faculty", json={
        "name": "Prof. Unauthorized",
        "email": "unauth@edunova.edu",
        "password": "testpassword123"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_forbidden.status_code == 403

    # 2. Admin creates faculty
    new_email = "testfaculty.aids@edunova.edu"
    db = SessionLocal()
    # Clean up previous test record if exists
    existing = db.query(Faculty).filter(Faculty.email == new_email).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.close()

    res_create = client.post("/faculty", json={
        "name": "Prof. AI Test",
        "email": new_email,
        "faculty_id": "FAC-TEST-01",
        "password": "password123",
        "department": "AI&DS",
        "expertise": ["Deep Learning", "NLP"],
        "max_hours": 18
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_create.status_code == 200
    new_faculty = res_create.get_json()
    new_id = new_faculty["id"]
    assert new_faculty["name"] == "Prof. AI Test"
    assert "Deep Learning" in new_faculty["expertise"]

    # 3. Admin updates faculty
    res_update = client.put(f"/faculty/{new_id}", json={
        "name": "Prof. AI Test Updated",
        "email": new_email,
        "role": "faculty",
        "department": "AI&DS",
        "max_hours": 20,
        "expertise": ["Deep Learning", "NLP", "Robotics"]
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_update.status_code == 200
    updated = res_update.get_json()
    assert updated["name"] == "Prof. AI Test Updated"
    assert updated["max_hours"] == 20

    # 4. Admin deactivates faculty
    res_delete = client.delete(f"/faculty/{new_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_delete.status_code == 200

    # Verify deactivated faculty is inactive
    db = SessionLocal()
    try:
        f_record = db.get(Faculty, new_id)
        assert f_record.active is False
        # Remove test record from DB so test is strictly idempotent
        db.delete(f_record)
        db.commit()
    finally:
        db.close()


# ============================================================================
# 6. TIMETABLE CRUD & CLASH DETECTION
# ============================================================================

def test_timetable_filtering(client, admin_token, faculty_token):
    # Filter by class_name
    res = client.get("/timetable?class_name=SY-AD1", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) >= 1
    for row in data:
        assert row["class_name"] == "SY-AD1"

    # Filter by day
    res_day = client.get("/timetable?day=Monday", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_day.status_code == 200
    for row in res_day.get_json():
        assert row["day"] == "Monday"

    # Search filter
    res_search = client.get("/timetable?search=Machine", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_search.status_code == 200
    search_data = res_search.get_json()
    assert any("Machine" in item["subject"] for item in search_data)


def test_timetable_clash_detection_on_create(client, admin_token):
    # In edunova.db: Monday 09:00 - 10:00: Machine Learning, TY-AD1, Room 101, Dr. Sharma (id=2)

    # 1. Faculty Clash (Dr. Sharma scheduled at same time elsewhere)
    res_fac_clash = client.post("/timetable", json={
        "day": "Monday",
        "start_time": "09:00",
        "end_time": "10:00",
        "subject": "Overlapping Subject",
        "class_name": "BE-AD1",
        "room": "Room 103",
        "faculty_id": 2
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_fac_clash.status_code == 409
    assert "Faculty is already scheduled" in str(res_fac_clash.get_json())

    # 2. Room Clash (Room 101 occupied at same time)
    res_room_clash = client.post("/timetable", json={
        "day": "Monday",
        "start_time": "09:00",
        "end_time": "10:00",
        "subject": "Room Overlap Subject",
        "class_name": "BE-AD1",
        "room": "Room 102",
        "faculty_id": 3
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_room_clash.status_code == 409
    assert "Room is already occupied" in str(res_room_clash.get_json())

    # 3. Class Clash (TY-AD1 already has a lecture at same time)
    res_class_clash = client.post("/timetable", json={
        "day": "Monday",
        "start_time": "09:00",
        "end_time": "10:00",
        "subject": "Class Overlap Subject",
        "class_name": "TY-AD1",
        "room": "Room 104",
        "faculty_id": 3
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_class_clash.status_code == 409
    assert "Class already has another lecture" in str(res_class_clash.get_json())


def test_timetable_create_and_delete_success(client, admin_token):
    # Free time: Thursday 15:00 - 16:00
    res_create = client.post("/timetable", json={
        "day": "Thursday",
        "start_time": "15:00",
        "end_time": "16:00",
        "subject": "Cloud Computing",
        "class_name": "BE-AD2",
        "room": "Room 104",
        "faculty_id": 3,
        "is_lab": False
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_create.status_code == 200
    new_entry = res_create.get_json()
    entry_id = new_entry["id"]

    # Delete entry
    res_del = client.delete(f"/timetable/{entry_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_del.status_code == 200


def test_clashes_checker_endpoint(client, faculty_token):
    res = client.get("/timetable/clashes/check", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert "total_clashes" in data
    assert "status" in data
    assert data["status"] in ("PASS", "CONFLICT")


# ============================================================================
# 7. ROOM OCCUPANCY & AVAILABILITY
# ============================================================================

def test_room_occupancy(client, faculty_token):
    res = client.get("/rooms/occupancy?day=Monday&start_time=09:00&end_time=10:00",
                     headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert "occupied_rooms" in data
    assert "available_rooms" in data
    occupied_names = [r["room_name"] for r in data["occupied_rooms"]]
    assert any(name in occupied_names for name in ["Room 102", "Room 101"])


# ============================================================================
# 8. SUBSTITUTES & AVAILABILITY
# ============================================================================

def test_substitute_recommendation(client, faculty_token):
    # Dr. Sharma (faculty id 2) scheduled for lecture id 1 (Monday 09:00 - 10:00)
    res = client.get("/substitutes/recommend?timetable_id=1",
                     headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert "recommendations" in data
    assert data["subject"] == "Machine Learning"


def test_substitute_request_workflow(client, faculty_token, second_faculty_token):
    # Dr. Sharma requests Prof. Patil (id=3) as substitute for lecture id 1
    res_req = client.post("/substitutes/request", json={
        "timetable_id": 1,
        "recommended_id": 3,
        "reason": "Attending university conference"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_req.status_code == 200
    req_data = res_req.get_json()
    req_id = req_data["request_id"]
    assert req_data["status"] == "Pending"

    # Prof. Patil responds to the request
    res_update = client.put(f"/substitutes/request/{req_id}", json={
        "status": "Accepted"
    }, headers={"Authorization": f"Bearer {second_faculty_token}"})
    assert res_update.status_code == 200
    assert res_update.get_json()["status"] == "Accepted"

    # Cleanup substitute request to keep database pure
    db = SessionLocal()
    try:
        sub = db.get(SubstituteRequest, req_id)
        if sub:
            db.delete(sub)
            db.commit()
    finally:
        db.close()


# ============================================================================
# 9. ANALYTICS (WORKLOAD, SYLLABUS & DASHBOARD)
# ============================================================================

def test_workload_analytics(client, admin_token, faculty_token):
    # Faculty workload (own only)
    res_f = client.get("/analytics/workload", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_f.status_code == 200
    data_f = res_f.get_json()
    assert len(data_f["faculty_workload"]) == 1

    # Admin workload (department-wide)
    res_a = client.get("/analytics/workload", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_a.status_code == 200
    data_a = res_a.get_json()
    assert len(data_a["faculty_workload"]) >= 6


def test_syllabus_analytics(client, faculty_token):
    res = client.get("/analytics/syllabus", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert "subjects" in data
    for s in data["subjects"]:
        assert "progress_percentage" in s


def test_dashboard_analytics(client, admin_token, faculty_token):
    res_admin = client.get("/analytics/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    assert "faculty_count" in res_admin.get_json()

    res_fac = client.get("/analytics/dashboard", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_fac.status_code == 200
    assert "assigned_classes" in res_fac.get_json()
