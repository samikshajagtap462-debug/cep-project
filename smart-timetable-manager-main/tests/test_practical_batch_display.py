import pytest
from backend.app.database import SessionLocal
from backend.app.models import TimetableEntry, Faculty, SubstituteRequest
from backend.app.formatters import format_display_class, extract_batch_letter, normalize_batch


def test_formatter_practical_and_theory():
    # 1. Practicals with Batch A, B, C
    assert format_display_class("SY-AD1", "Batch A", is_lab=True) == "SY AD1 (A)"
    assert format_display_class("SY-AD1", "Batch B", is_lab=True) == "SY AD1 (B)"
    assert format_display_class("SY-AD1", "Batch C", is_lab=True) == "SY AD1 (C)"

    # All valid TY and BE divisions
    assert format_display_class("TY-AD1", "Batch A", is_lab=True) == "TY AD1 (A)"
    assert format_display_class("TY-AD2", "Batch B", is_lab=True) == "TY AD2 (B)"
    assert format_display_class("BE-AD1", "A", is_lab=True) == "BE AD1 (A)"
    assert format_display_class("BE-AD2", "Batch C", is_lab=True) == "BE AD2 (C)"

    # 2. Theory lecture without batch
    assert format_display_class("SY-AD1", None, is_lab=False) == "SY AD1"
    assert format_display_class("TY-AD1", None, is_lab=False) == "TY AD1"
    assert format_display_class("BE-AD1", None, is_lab=False) == "BE AD1"

    # 3. Practical missing batch flags for correction
    assert format_display_class("SY-AD1", None, is_lab=True) == "SY AD1 (Batch Required)"

    # 4. Batch letters extraction without false positives
    assert extract_batch_letter("Batch A") == "A"
    assert extract_batch_letter("Batch B") == "B"
    assert extract_batch_letter("Batch C") == "C"
    assert extract_batch_letter("A") == "A"
    assert extract_batch_letter("B") == "B"
    assert extract_batch_letter("C") == "C"


def test_api_sy_ad1_practical_batches_abc(client, faculty_token):
    """Test Case 1, 2, 3: Practical assigned to SY AD1 batches A, B, C displays SY AD1 (A), (B), (C)."""
    res = client.get("/api/classes/SY-AD1/timetable", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    entries = res.get_json()

    practicals = [e for e in entries if e["is_lab"]]
    assert len(practicals) >= 21

    batch_a_practicals = [e for e in practicals if extract_batch_letter(e.get("batch")) == "A"]
    batch_b_practicals = [e for e in practicals if extract_batch_letter(e.get("batch")) == "B"]
    batch_c_practicals = [e for e in practicals if extract_batch_letter(e.get("batch")) == "C"]

    assert len(batch_a_practicals) == 7
    assert len(batch_b_practicals) == 7
    assert len(batch_c_practicals) == 7

    for p in batch_a_practicals:
        assert p["classDiv"] == "SY AD1 (A)", f"Expected 'SY AD1 (A)', got '{p['classDiv']}'"

    for p in batch_b_practicals:
        assert p["classDiv"] == "SY AD1 (B)", f"Expected 'SY AD1 (B)', got '{p['classDiv']}'"

    for p in batch_c_practicals:
        assert p["classDiv"] == "SY AD1 (C)", f"Expected 'SY AD1 (C)', got '{p['classDiv']}'"


def test_api_ty_and_be_practical_batches(client, faculty_token, admin_token):
    """Test Case 4: Practical batch display for TY and BE divisions."""
    # Check existing TY-AD1 practicals in DB
    res = client.get("/api/classes/TY-AD1/timetable", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    entries = res.get_json()
    ty_practicals = [e for e in entries if e["is_lab"]]
    assert len(ty_practicals) >= 18

    for p in ty_practicals:
        b_letter = p.get("batch_letter") or extract_batch_letter(p.get("batch"))
        assert p["classDiv"] == f"TY AD1 ({b_letter})"

    # Test creating a practical for BE-AD1 and BE-AD2
    res_be = client.post("/api/timetable", json={
        "day": "Saturday",
        "start_time": "10:15",
        "end_time": "12:15",
        "subject": "Deep Learning Laboratory",
        "class_name": "BE-AD1",
        "room": "AI1",
        "faculty_id": 2,
        "batch": "Batch A",
        "is_lab": True,
        "session_type": "Practical"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_be.status_code == 200
    be_data = res_be.get_json()
    assert be_data["classDiv"] == "BE AD1 (A)"
    assert be_data["batch"] == "Batch A"
    assert be_data["batch_letter"] == "A"

    # Cleanup
    client.delete(f"/timetable/{be_data['id']}", headers={"Authorization": f"Bearer {admin_token}"})


def test_theory_lecture_displays_without_batch(client, faculty_token):
    """Test Case 5: Theory lecture assigned to SY AD1 displays 'SY AD1' without unnecessary batch."""
    res = client.get("/api/classes/SY-AD1/timetable", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    entries = res.get_json()
    theories = [e for e in entries if not e["is_lab"]]
    assert len(theories) >= 12

    for t in theories:
        assert t["classDiv"] == "SY AD1"
        assert "(" not in t["classDiv"]
        assert ")" not in t["classDiv"]


def test_admin_and_faculty_views_show_identical_class_and_batch(client, admin_token, faculty_token):
    """Test Case 6: Admin and faculty views show the same class and batch for the same session."""
    res_admin = client.get("/api/admin/timetable?class_name=SY-AD1", headers={"Authorization": f"Bearer {admin_token}"})
    res_fac = client.get("/api/timetable?class_name=SY-AD1", headers={"Authorization": f"Bearer {faculty_token}"})

    assert res_admin.status_code == 200
    assert res_fac.status_code == 200

    admin_map = {e["id"]: e for e in res_admin.get_json()}
    fac_map = {e["id"]: e for e in res_fac.get_json()}

    common_ids = set(admin_map.keys()) & set(fac_map.keys())
    assert len(common_ids) >= 20

    for eid in common_ids:
        a = admin_map[eid]
        f = fac_map[eid]
        assert a["classDiv"] == f["classDiv"]
        assert a["batch"] == f["batch"]
        assert a["subject"] == f["subject"]


def test_editing_and_saving_practical_preserves_batch(client, admin_token):
    """Test Case 7: Editing and saving a practical preserves its batch."""
    # Fetch an existing practical session
    res = client.get("/api/admin/timetable?class_name=SY-AD1", headers={"Authorization": f"Bearer {admin_token}"})
    practicals = [e for e in res.get_json() if e["is_lab"]]
    target = practicals[0]
    target_id = target["id"]
    original_batch = target["batch"]
    original_room = target["room"]

    # 1. Update room, preserve batch
    res_edit = client.put(f"/api/timetable/{target_id}", json={
        "room": "Lab 201",
        "batch": original_batch
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_edit.status_code == 200
    data = res_edit.get_json()
    assert data["batch"] == original_batch
    b_let = extract_batch_letter(original_batch)
    assert data["classDiv"] == f"SY AD1 ({b_let})"
    assert data["room"] == "Lab 201"

    # Restore original room
    client.put(f"/api/timetable/{target_id}", json={
        "room": original_room,
        "batch": original_batch
    }, headers={"Authorization": f"Bearer {admin_token}"})


def test_substitute_allocation_preserves_class_and_batch(client, faculty_token, admin_token):
    """Test Case 8: Substitute allocation preserves original class division and batch."""
    # Find a lecture belonging to faculty 7 (Mrs. Ashvini N. Ahirrao)
    db = SessionLocal()
    fac7 = db.query(Faculty).filter(Faculty.email == "ana@edunova.edu").first()
    tt_entry = db.query(TimetableEntry).filter(
        TimetableEntry.faculty_id == fac7.id,
        TimetableEntry.is_lab == True
    ).first()
    db.close()

    # Log in as faculty 7
    login_fac = client.post("/api/auth/login", json={"email": "ana@edunova.edu", "password": "faculty123"})
    assert login_fac.status_code == 200
    ana_token = login_fac.get_json()["access_token"]

    # Submit substitute request
    res_sub = client.post("/substitutes/request", json={
        "timetable_id": tt_entry.id,
        "recommended_id": 8,  # Mrs. Abhilasha S. Shinde
        "reason": "Academic leave for department symposium"
    }, headers={"Authorization": f"Bearer {ana_token}"})
    assert res_sub.status_code == 200
    sub_data = res_sub.get_json()
    sub_id = sub_data["request_id"]

    # Query substitute requests
    res_list = client.get("/api/substitutes/requests", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_list.status_code == 200
    all_reqs = res_list.get_json()
    created_req = next((r for r in all_reqs if r["id"] == sub_id), None)
    assert created_req is not None

    b_let = extract_batch_letter(tt_entry.batch)
    expected_class = f"SY AD1 ({b_let})"
    assert created_req["class_name"] == expected_class
    assert created_req["classDiv"] == expected_class

    # Cleanup substitute request
    db = SessionLocal()
    req_obj = db.get(SubstituteRequest, sub_id)
    if req_obj:
        db.delete(req_obj)
        db.commit()
    db.close()


def test_batch_conflict_detection_and_parallel_practicals(client, admin_token):
    """
    Test Case 10:
    - Same batch at same time -> 409 conflict.
    - Different batches (Batch A in AI1 and Batch B in AI2) at same time with different faculty -> ALLOWED!
    """
    # 1. Schedule Session 1: Batch A on Saturday 08:00-10:00, Room AI1, Faculty 7
    res1 = client.post("/api/timetable", json={
        "day": "Saturday",
        "start_time": "08:00",
        "end_time": "10:00",
        "subject": "Parallel Practical Lab 1",
        "class_name": "SY-AD1",
        "room": "AI1",
        "faculty_id": 7,
        "batch": "Batch A",
        "is_lab": True,
        "session_type": "Practical"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res1.status_code == 200
    s1_id = res1.get_json()["id"]

    try:
        # 2. Attempt conflict: Same Batch A at same time in Room AI2 with Faculty 8 -> MUST FAIL 409
        res_conflict = client.post("/api/timetable", json={
            "day": "Saturday",
            "start_time": "08:00",
            "end_time": "10:00",
            "subject": "Conflicting Batch A Lab",
            "class_name": "SY-AD1",
            "room": "AI2",
            "faculty_id": 8,
            "batch": "Batch A",
            "is_lab": True,
            "session_type": "Practical"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert res_conflict.status_code == 409

        # 3. Parallel Practical: Batch B at same time in Room AI2 with Faculty 8 -> MUST SUCCEED 200
        res2 = client.post("/api/timetable", json={
            "day": "Saturday",
            "start_time": "08:00",
            "end_time": "10:00",
            "subject": "Parallel Practical Lab 2",
            "class_name": "SY-AD1",
            "room": "AI2",
            "faculty_id": 8,
            "batch": "Batch B",
            "is_lab": True,
            "session_type": "Practical"
        }, headers={"Authorization": f"Bearer {admin_token}"})
        assert res2.status_code == 200
        s2_id = res2.get_json()["id"]
        assert res2.get_json()["classDiv"] == "SY AD1 (B)"

        # Cleanup s2
        client.delete(f"/timetable/{s2_id}", headers={"Authorization": f"Bearer {admin_token}"})

    finally:
        # Cleanup s1
        client.delete(f"/timetable/{s1_id}", headers={"Authorization": f"Bearer {admin_token}"})
