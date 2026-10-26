import pytest
import re
import os
from backend.app.models import Faculty, TimetableEntry, Room, ClassModel, Batch, Subject
from backend.app.database import SessionLocal


def test_classes_and_divisions_removed_from_admin_ui():
    """Verify that Classes & Divisions management UI is removed from admin.html,

    while preserving backend models and database records.
    """
    admin_html_path = os.path.abspath("smart-timetable-manager-main/admin.html")
    if not os.path.exists(admin_html_path):
        admin_html_path = os.path.abspath("admin.html")

    with open(admin_html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Verify nav button and section are removed
    assert 'id="nav-classes"' not in content, "nav-classes should be removed from admin.html"
    assert 'id="section-classes"' not in content, "section-classes should be removed from admin.html"
    assert 'renderClassesAndDivisions' not in content, "renderClassesAndDivisions function should be removed"
    assert 'admin-classes-container' not in content, "admin-classes-container should be removed"

    # 2. Verify backend classes endpoint still works for timetable scheduling
    db = SessionLocal()
    try:
        classes = db.query(ClassModel).all()
        assert len(classes) == 7, "All 7 AIDS classes must remain intact in database"
        batches = db.query(Batch).all()
        assert len(batches) == 21, "All 21 practical batches must remain intact in database"
    finally:
        db.close()


def test_hod_admin_account_separation(client, admin_token, faculty_token):
    """Verify Dr. Dhanraj R. Dhotre is designated as HOD/Admin,

    is excluded from ordinary teaching rosters, while preserving his verified teaching assignments.
    """
    db = SessionLocal()
    try:
        # 1. Verify HOD account configuration
        hod = db.query(Faculty).filter(Faculty.faculty_id == "FAC-DRD").first()
        assert hod is not None, "Dr. Dhanraj R. Dhotre must exist in faculty table"
        assert hod.role == "admin", "Dr. Dhanraj R. Dhotre must have role='admin'"
        assert hod.email == "drdhotre@edunova.edu"

        # 2. Verify legitimate teaching assignments exist and are preserved
        hod_entries = db.query(TimetableEntry).filter(TimetableEntry.faculty_id == hod.id).all()
        assert len(hod_entries) == 3, "Dr. Dhotre must retain his 3 verified teaching sessions"
        for entry in hod_entries:
            assert entry.subject == "Scientific Research & Publication"
            assert entry.room == "IIOT"
            assert entry.class_name == "SY-AD1"
            assert entry.batch in ("Batch A", "Batch B", "Batch C")
    finally:
        db.close()

    # 3. Test Admin Dashboard API separates teaching faculty from admin
    res_dash = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_dash.status_code == 200
    dash_data = res_dash.get_json()
    assert dash_data["total_teaching_faculty"] == 22
    assert dash_data["total_admin_accounts"] >= 1

    # Faculty summary roster in dashboard contains teaching faculty, excluding admin
    summary_roles = [f["role"] for f in dash_data["faculty_summary"]]
    assert "admin" not in summary_roles

    # HOD teaching verification is explicitly reported
    assert "hod_teaching_verification" in dash_data
    assert len(dash_data["hod_teaching_verification"]) >= 1
    assert dash_data["hod_teaching_verification"][0]["verified"] is True
    assert dash_data["hod_teaching_verification"][0]["sessions_count"] == 3

    # 4. Verify admin endpoints are protected against non-admin access
    res_forbidden = client.get("/api/admin/dashboard", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_forbidden.status_code in (401, 403)


def test_occupied_labs_feature(client, admin_token, faculty_token):
    """Verify laboratory occupancy with interval overlap and practical batch display."""
    # Monday 08:00 - 10:00 has multiple occupied labs in database:
    # AI1, ARVR, CN1, IOT, Room 609A, Room 609B
    res = client.get("/rooms/occupancy?day=Monday&start_time=08:00&end_time=10:00",
                     headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.get_json()

    occupied_names = [r["room_name"] for r in data["occupied_rooms"]]
    assert "AI1" in occupied_names
    assert any(name in occupied_names for name in ["Lab 609A", "Room 609A"])

    # Check rich details for AI1
    ai1_room = next(r for r in data["occupied_rooms"] if r["room_name"] == "AI1")
    assert ai1_room["status"] == "Occupied"
    assert ai1_room["is_lab"] is True
    assert ai1_room["session"] is not None
    assert "TY AD1 (B)" in ai1_room["session"]["class_div"]
    assert ai1_room["session"]["subject"] == "Engineering Design and Innovation-I"
    assert ai1_room["session"]["faculty_name"] == "Ms. Avani Anawardekar"

    # Test interval overlap: partial overlap with 08:00-10:00 session (09:00 - 10:00)
    res_overlap = client.get("/rooms/occupancy?day=Monday&start_time=09:00&end_time=10:00",
                             headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_overlap.status_code == 200
    data_overlap = res_overlap.get_json()
    overlap_names = [r["room_name"] for r in data_overlap["occupied_rooms"]]
    # AI1 session runs 08:00 to 10:00, so it must be marked Occupied for 09:00-10:00 interval
    assert "AI1" in overlap_names

    # Test HOD's practical session on Monday 15:15 - 17:15 in IIOT lab
    res_hod = client.get("/rooms/occupancy?day=Monday&start_time=15:15&end_time=17:15",
                         headers={"Authorization": f"Bearer {admin_token}"})
    assert res_hod.status_code == 200
    hod_occ = res_hod.get_json()
    iiot_room = next((r for r in hod_occ["occupied_rooms"] if r["room_name"] == "IIOT"), None)
    assert iiot_room is not None
    assert "SY AD1 (C)" in iiot_room["session"]["class_div"]
    assert iiot_room["session"]["faculty_name"] == "Dr. Dhanraj R. Dhotre"

    # Test genuine empty state: Sunday has no timetable sessions
    res_empty = client.get("/rooms/occupancy?day=Sunday&start_time=08:00&end_time=10:00",
                           headers={"Authorization": f"Bearer {admin_token}"})
    assert res_empty.status_code == 200
    data_empty = res_empty.get_json()
    assert len(data_empty["occupied_rooms"]) == 0
    assert len(data_empty["available_rooms"]) >= 10


def test_reports_and_analytics_comprehensive(client, admin_token, faculty_token):
    """Verify that reports & analytics return accurate, database-verified counts,

    with non-zero sessions and precise theory vs practical calculations.
    """
    res = client.get("/api/analytics/reports", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.get_json()

    # 1. Total session counts matching master database
    assert data["total_sessions"] in (135, 136)
    assert data["theory_sessions"] in (54, 55)
    assert data["practical_sessions"] == 81
    assert data["total_teaching_hours"] in (221.0, 222.0)
    assert data["theory_hours"] in (59.0, 60.0)
    assert data["practical_hours"] == 162.0

    # 2. Teaching faculty roster: 22 members, admin excluded from teaching totals
    assert data["total_teaching_faculty"] == 22
    assert len(data["workload_summary"]) == 22
    # Ensure all entries have valid non-zero or calculated hours
    fac_names = [f["name"] for f in data["workload_summary"]]
    assert "Admin" not in fac_names
    assert "Mrs. Ashvini N. Ahirrao" in fac_names

    # Check Mrs. Ashvini N. Ahirrao's workload
    ana = next(f for f in data["workload_summary"] if f["name"] == "Mrs. Ashvini N. Ahirrao")
    assert ana["total_sessions"] == 9
    assert ana["total_hours"] >= 10

    # 3. Class breakdown includes all cohorts and practical batches A, B, C
    assert len(data["class_breakdown"]) == 7
    class_map = {c["class_name"]: c for c in data["class_breakdown"]}
    assert "SY-AD1" in class_map
    assert class_map["SY-AD1"]["total_sessions"] in (33, 34)
    assert class_map["SY-AD1"]["batches"]["Batch A"] == 7
    assert class_map["SY-AD1"]["batches"]["Batch B"] == 7
    assert class_map["SY-AD1"]["batches"]["Batch C"] == 7

    # 4. Subject breakdown
    assert len(data["subject_breakdown"]) >= 10
    subj_map = {s["name"]: s for s in data["subject_breakdown"]}
    assert "Scientific Research & Publication" in subj_map
    assert subj_map["Scientific Research & Publication"]["total_sessions"] == 9

    # 5. Day breakdown
    day_map = {d["day"]: d for d in data["day_breakdown"]}
    assert day_map["Monday"]["total_sessions"] in (33, 34)
    assert day_map["Wednesday"]["total_sessions"] == 32
    assert day_map["Thursday"]["total_sessions"] == 28
    assert day_map["Tuesday"]["total_sessions"] == 22
    assert day_map["Friday"]["total_sessions"] == 20

    # 6. HOD verification details
    assert len(data["hod_teaching_verification"]) >= 1
    assert data["hod_teaching_verification"][0]["sessions_count"] == 3
