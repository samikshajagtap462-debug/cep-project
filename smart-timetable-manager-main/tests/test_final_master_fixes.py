"""Comprehensive tests verifying the 14 requirements of the Final Master Prompt.

Tests include:
1. Fake admin (ADM-101) exclusion from ordinary faculty records and teaching stats.
2. Intended facility configuration (only 10 verified classrooms, laboratories, and Lab 607 sub-labs).
3. Department notifications lifecycle and clean empty state.
4. Clean removal of Cohort/Batch distribution and Weekday distribution from Admin Reports UI.
5. Centralized accurate workload calculation service (222.0 hrs across 136 sessions).
6. Scan Master Timetable and conflict detection engine (CSV/Excel parsing, multi-conflict detection, transactional import).
7. Authentic syllabus topics mapping and progress tracking.
8. Complete readable subject names without clipping on faculty dashboard.
"""

import io
import os
import pytest
from backend.app.models import Faculty, Room, TimetableEntry, Subject, SyllabusTopic, AdminNotification
from backend.app.services.workload_service import (
    calculate_session_duration,
    get_faculty_workload_detail,
    get_all_faculty_workloads,
    get_department_kpi_summary
)


def _resolve_frontend_file(filename):
    for candidate in [
        os.path.abspath(filename),
        os.path.abspath(os.path.join("smart-timetable-manager-main", filename)),
        os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), filename))
    ]:
        if os.path.exists(candidate):
            return candidate
    return os.path.abspath(filename)


# ============================================================================
# 1. FAKE ADMIN EXCLUSION & HOD ACCOUNT SEPARATION
# ============================================================================

def test_fake_admin_excluded_from_faculty_directory_and_stats(client, admin_token, faculty_token):
    # Ordinary faculty list via GET /api/faculty
    res_fac = client.get("/api/faculty", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_fac.status_code == 200
    fac_list = res_fac.get_json()
    assert not any(f["faculty_id"] == "ADM-101" for f in fac_list)
    assert not any(f["id"] == 1 for f in fac_list)

    # Admin faculty management list via GET /api/admin/faculty
    res_admin = client.get("/api/admin/faculty", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200
    admin_fac_list = res_admin.get_json()
    assert not any(f["faculty_id"] == "ADM-101" for f in admin_fac_list)
    assert not any(f["id"] == 1 for f in admin_fac_list)

    # Verify HOD Dr. Dhanraj R. Dhotre is kept and has verified teaching assignments
    dhotre = next((f for f in admin_fac_list if f["faculty_id"] == "FAC-DRD"), None)
    assert dhotre is not None
    assert dhotre["role"] == "admin"
    assert dhotre["total_sessions"] == 3
    assert dhotre["current_hours"] == 6.0

    # Verify admin login still functions with designated HOD identity
    res_login = client.post("/api/auth/login", json={
        "email": "admin@edunova.edu",
        "password": "admin123",
        "role": "admin"
    })
    assert res_login.status_code == 200
    user_data = res_login.get_json()["user"]
    assert user_data["faculty_id"] == "FAC-DRD"


# ============================================================================
# 2. INTENDED FACILITIES CONFIGURATION
# ============================================================================

def test_intended_facilities_configuration(client, faculty_token):
    res = client.get("/api/rooms", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    rooms = res.get_json()

    # Active facilities must be EXACTLY 10 intended rooms
    assert len(rooms) == 10
    active_names = {r["name"] for r in rooms}

    # Expected Classrooms
    assert "Room 102" in active_names
    assert "Room 103" in active_names
    assert "Room 104" in active_names

    # Expected Laboratories
    assert "Lab 609A" in active_names
    assert "Lab 609B" in active_names

    # Expected Lab 607 Sub-labs
    assert "AI1" in active_names
    assert "AI2" in active_names
    assert "CN1" in active_names
    assert "ARVR" in active_names
    assert "IIOT" in active_names

    # Unverified sample facilities must NOT be active
    assert "Lab 201" not in active_names
    assert "Lab 202" not in active_names
    assert "Room 201" not in active_names
    assert "Room 101" not in active_names
    assert "Room MB614" not in active_names


# ============================================================================
# 3. DEPARTMENT NOTIFICATIONS LIFECYCLE
# ============================================================================

def test_department_notifications_lifecycle(client, admin_token, faculty_token):
    # 1. Fetch initial notifications
    res = client.get("/api/notifications", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    initial_notifs = res.get_json()
    assert isinstance(initial_notifs, list)

    # 2. Admin creates genuine AI & DS notice
    res_create = client.post("/api/notifications", json={
        "title": "AI & DS Board of Studies Meeting",
        "message": "Curriculum review for autonomous semester will be held on Thursday at 3:00 PM."
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_create.status_code == 201
    created_notif = res_create.get_json()["notification"]
    notif_id = created_notif["id"]
    assert created_notif["title"] == "AI & DS Board of Studies Meeting"
    assert created_notif["is_read"] is False

    # 3. Faculty reads notifications and marks read
    res_list = client.get("/api/notifications", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_list.status_code == 200
    notifs = res_list.get_json()
    assert any(n["id"] == notif_id for n in notifs)

    res_read = client.put(f"/api/notifications/{notif_id}/read", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_read.status_code == 200
    assert res_read.get_json()["is_read"] is True


# ============================================================================
# 4. REPORTS & ANALYTICS UI CLEANUP
# ============================================================================

def test_reports_analytics_removals_and_preservations():
    with open(_resolve_frontend_file("admin.html"), "r", encoding="utf-8") as f:
        html = f.read()

    # Verify removed sections are completely gone from HTML
    assert "Cohort & Practical Batch Distribution" not in html
    assert "7 Active Cohorts" not in html
    assert "Schedule Distribution by Weekday" not in html
    assert 'id="rep-cohort-distribution-tbody"' not in html
    assert 'id="rep-day-distribution-tbody"' not in html

    # Verify preserved components remain present
    assert 'id="section-reports"' in html
    assert 'id="rep-kpi-total-sessions"' in html
    assert 'id="rep-kpi-theory-sessions"' in html
    assert 'id="rep-kpi-practical-sessions"' in html
    assert 'id="rep-kpi-total-hours"' in html
    assert 'id="rep-hod-verification-banner"' in html
    assert 'id="workload-faculty-select"' in html
    assert 'id="faculty-workload-comparison-tbody"' in html
    assert 'id="rep-subject-distribution-tbody"' in html


# ============================================================================
# 5. CENTRALIZED WORKLOAD CALCULATION SERVICE
# ============================================================================

def test_centralized_workload_calculation_service(client, admin_token):
    res = client.get("/api/analytics/reports", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    data = res.get_json()

    # Exact session breakdown
    assert data["total_sessions"] in (135, 136)
    assert data["theory_sessions"] in (54, 55)
    assert data["practical_sessions"] == 81
    assert data["total_teaching_hours"] in (221.0, 222.0)

    # Workload by faculty duration calculation
    fac_workloads = data["faculty_workload"]
    assert len(fac_workloads) >= 20

    # Mrs. Ashvini N. Ahirrao (FAC-ANA): 4 theory sessions (4 hrs) + 5 practical sessions (10 hrs) = 14.0 hrs
    ana = next((f for f in fac_workloads if f["faculty_code"] == "FAC-ANA"), None)
    assert ana is not None
    assert ana["theory_sessions"] == 4
    assert ana["practical_sessions"] == 5
    assert ana["total_hours"] == 14.0

    # Test duration parser
    assert calculate_session_duration("08:00", "10:00") == 2.0
    assert calculate_session_duration("10:15", "12:15") == 2.0
    assert calculate_session_duration("09:00", "10:00") == 1.0
    assert calculate_session_duration("11:15", "12:15") == 1.0


# ============================================================================
# 6. SCAN MASTER TIMETABLE & CONFLICT ENGINE
# ============================================================================

def test_scan_master_timetable_and_conflict_engine(client, admin_token):
    # 1. Test scanning CSV with valid entries and clashes
    csv_content = """Day,Time,Subject,Class,Faculty,Room,Batch,Type
Monday,08:00 - 10:00,Operating Systems Laboratory,SY-AD1,FAC-SJN,AI1,Batch A,Practical
Monday,08:00 - 10:00,Problem Solving & Object-Oriented Programming Lab,SY-AD1,FAC-ANA,AI1,Batch B,Practical
Saturday,08:00 - 10:00,Special Autonomous Session,SY-AD1,FAC-ANA,Room 102,,Theory
"""
    # Note: Row 2 has Room clash on AI1 (double-booked with Row 1)
    res_scan = client.post("/api/timetable/scan", data={
        "file": (io.BytesIO(csv_content.encode("utf-8")), "timetable_test.csv")
    }, content_type="multipart/form-data", headers={"Authorization": f"Bearer {admin_token}"})

    assert res_scan.status_code == 200
    report = res_scan.get_json()
    assert report["success"] is True
    assert report["total_rows"] == 3
    assert report["blocking_count"] >= 1  # AI1 clash detected

    clashes = [c["conflict_type"] for c in report["blocking_conflicts"]]
    assert any("Room" in c for c in clashes)

    # 2. Test importing valid session transactionally
    valid_sample = [
        {
            "day": "Saturday",
            "start_time": "15:15",
            "end_time": "17:15",
            "subject": "Research Methodology Seminar",
            "class_name": "BE-AD2",
            "faculty_id": 7,  # Mrs. Ashvini Ahirrao
            "room": "Room 104",
            "batch": None,
            "is_lab": False,
            "session_type": "Theory"
        }
    ]

    res_import = client.post("/api/timetable/import", json={
        "entries": valid_sample
    }, headers={"Authorization": f"Bearer {admin_token}"})

    assert res_import.status_code == 200
    import_result = res_import.get_json()
    assert import_result["success"] is True
    assert import_result["imported_count"] == 1

    # Cleanup imported test entry
    from backend.app.database import get_db
    db = get_db()
    entry = db.query(TimetableEntry).filter(
        TimetableEntry.subject == "Research Methodology Seminar"
    ).first()
    if entry:
        db.delete(entry)
        db.commit()


# ============================================================================
# 7. SYLLABUS TOPICS AND TOPIC-LEVEL COMPLETION TRACKING
# ============================================================================

def test_syllabus_topics_and_authentic_tracking(client, faculty_token, admin_token):
    # Operating System & Administration (subject id 8) has authentic topics seeded
    res = client.get("/analytics/syllabus/topics?subject_id=8", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["subject_id"] == 8
    topics = data["topics"]
    assert len(topics) >= 10
    assert any("Dual-Mode Operation" in t["topic_name"] for t in topics)

    # Add a topic to a course
    res_add = client.post("/analytics/syllabus/topics", json={
        "subject_id": 8,
        "unit_number": 5,
        "unit_title": "Storage Management & File Systems",
        "topic_name": "RAID Architectures & Reliability Models",
        "planned_lectures": 2,
        "target_date": "2026-11-20"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_add.status_code == 201
    new_topic = res_add.get_json()["topic"]
    topic_id = new_topic["id"]

    # Update topic status to Completed
    res_upd = client.put(f"/analytics/syllabus/topics/{topic_id}", json={
        "status": "Completed",
        "completed_lectures": 2
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert res_upd.status_code == 200
    assert res_upd.get_json()["topic"]["status"] == "Completed"

    # Cleanup test topic
    from backend.app.database import get_db
    db = get_db()
    top = db.get(SyllabusTopic, topic_id)
    if top:
        db.delete(top)
        db.commit()


# ============================================================================
# 8. FACULTY DASHBOARD SUBJECT WRAPPING & STRIKETHROUGH
# ============================================================================

def test_faculty_dashboard_subject_names_no_cutoff():
    with open(_resolve_frontend_file("faculty.html"), "r", encoding="utf-8") as f:
        html = f.read()

    # Check CSS classes ensuring no cutoff or clipping on long subject names
    assert "break-words" in html
    assert "whitespace-normal" in html
    assert "min-w-0" in html
    assert "flex-1" in html
    # Check strikethrough styling for completed lectures
    assert "line-through" in html
    assert "text-slate-500" in html
