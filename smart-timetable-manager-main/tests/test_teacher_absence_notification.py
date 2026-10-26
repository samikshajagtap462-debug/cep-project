"""Test suite verifying Teacher Absence Notifications Delivery & Visibility to HOD.

Covers:
1. Teacher submits an absence notification via /api/notifications/absence.
2. Error handling: 400 for missing date or reason; 401 for unauthenticated submission.
3. Database storage & relational verification:
   - Associated with correct teacher (publisher_id == teacher.id).
   - Associated with teacher's department (department == teacher.department).
   - Associated with correct HOD (target_faculty_id == hod.id).
   - recipient_scope == "hod" and initial is_read == False.
4. HOD receives and views notification via GET /api/notifications.
5. Privacy protection: Other faculty members do NOT see the teacher's absence notice.
6. Submitting teacher can see their own notice in their notification list.
7. HOD can mark the absence notification as read via PUT /api/notifications/<id>/read.
8. Backward compatibility: Faculty submitting absence notice via POST /api/notifications is accepted.
9. Frontend wiring: faculty.html and admin.html have correct element IDs and function hooks.
"""

import os
import pytest
from backend.app.models import Faculty, AdminNotification, FacultyNotificationRead


def _resolve_file(filename):
    for candidate in [
        os.path.abspath(filename),
        os.path.abspath(os.path.join("smart-timetable-manager-main", filename)),
        os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), filename))
    ]:
        if os.path.exists(candidate):
            return candidate
    return os.path.abspath(filename)


# ============================================================================
# 1. TEACHER ABSENCE NOTIFICATION SUBMISSION & VALIDATION
# ============================================================================

def test_teacher_absence_notification_validation(client, faculty_token):
    """Validation: missing date or reason must return 400 Bad Request."""
    # 1. Missing date
    res1 = client.post("/api/notifications/absence", json={
        "leave_category": "Casual Leave (CL)",
        "reason": "Family emergency"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res1.status_code == 400
    assert "Date of leave is required" in res1.get_json()["detail"]

    # 2. Missing reason
    res2 = client.post("/api/notifications/absence", json={
        "date": "2026-11-05",
        "leave_category": "Casual Leave (CL)"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res2.status_code == 400
    assert "Reason for absence is required" in res2.get_json()["detail"]

    # 3. Unauthenticated request
    res3 = client.post("/api/notifications/absence", json={
        "date": "2026-11-05",
        "leave_category": "Casual Leave (CL)",
        "reason": "Medical appointment"
    })
    assert res3.status_code == 401


# ============================================================================
# 2. COMPLETE SUBMISSION TO HOD DELIVERY FLOW
# ============================================================================

def test_teacher_submits_absence_and_hod_receives_it(client, faculty_token, admin_token, second_faculty_token, app):
    """Trace complete absence notification flow from teacher to HOD."""
    test_date = "2026-11-12"
    test_cat = "Medical Leave (ML)"
    test_reason = "Scheduled surgical procedure and post-op recovery"

    # Step 1: Teacher submits absence notification
    res_submit = client.post("/api/notifications/absence", json={
        "date": test_date,
        "leave_category": test_cat,
        "reason": test_reason
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_submit.status_code in (200, 201)

    data = res_submit.get_json()
    assert data["success"] is True
    notif_data = data["notification"]
    notif_id = notif_data["id"]

    assert test_date in notif_data["message"]
    assert test_reason in notif_data["message"]
    assert test_cat in notif_data["title"] or test_cat in notif_data["message"]

    # Step 2: Verify database records & relationships
    with app.app_context():
        from backend.app.database import SessionLocal
        db = SessionLocal()
        try:
            db_notif = db.get(AdminNotification, notif_id)
            assert db_notif is not None

            # Associated with teacher
            teacher = db.get(Faculty, db_notif.publisher_id)
            assert teacher is not None
            assert teacher.role == "faculty"
            assert db_notif.publisher_id == teacher.id

            # Associated with department
            assert db_notif.department == teacher.department

            # Associated with HOD
            hod = db.get(Faculty, db_notif.target_faculty_id)
            assert hod is not None
            assert hod.role == "admin"
            assert hod.department == teacher.department

            # Recipient scope is hod
            assert db_notif.recipient_scope == "hod"
            assert db_notif.is_read is False
        finally:
            db.close()

    # Step 3: HOD receives and views the notification
    res_hod = client.get("/api/notifications", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_hod.status_code == 200
    hod_notifs = res_hod.get_json()

    # Must be in HOD's list
    matching_hod = next((n for n in hod_notifs if n["id"] == notif_id), None)
    assert matching_hod is not None
    assert matching_hod["is_read"] is False
    assert matching_hod["publisher_id"] == db_notif.publisher_id
    assert matching_hod["publisher_name"] == teacher.name
    assert test_date in matching_hod["message"]

    # Step 4: Privacy protection: Second faculty member does NOT receive this notice
    res_other = client.get("/api/notifications", headers={"Authorization": f"Bearer {second_faculty_token}"})
    assert res_other.status_code == 200
    other_notifs = res_other.get_json()
    assert not any(n["id"] == notif_id for n in other_notifs)

    # Step 5: Submitting teacher CAN see their own notice in their notification list
    res_self = client.get("/api/notifications", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_self.status_code == 200
    self_notifs = res_self.get_json()
    matching_self = next((n for n in self_notifs if n["id"] == notif_id), None)
    assert matching_self is not None

    # Step 6: HOD marks the notification as read
    res_read = client.put(f"/api/notifications/{notif_id}/read", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_read.status_code == 200
    assert res_read.get_json()["is_read"] is True

    # Step 7: HOD refreshes notifications - now marked as read
    res_hod_refreshed = client.get("/api/notifications", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_hod_refreshed.status_code == 200
    matching_read = next((n for n in res_hod_refreshed.get_json() if n["id"] == notif_id), None)
    assert matching_read is not None
    assert matching_read["is_read"] is True


# ============================================================================
# 3. BACKWARD COMPATIBILITY: FACULTY SUBMISSION VIA /api/notifications
# ============================================================================

def test_faculty_submission_via_generic_notifications_endpoint(client, faculty_token, admin_token):
    """Faculty can also submit absence notices through /api/notifications."""
    res = client.post("/api/notifications", json={
        "date": "2026-11-20",
        "leave_category": "Duty Leave (DL) - FDP / Seminar",
        "reason": "Faculty Development Program at IIT Bombay"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code in (200, 201)

    notif_id = res.get_json()["notification"]["id"]

    # HOD can see it
    res_hod = client.get("/api/notifications", headers={"Authorization": f"Bearer {admin_token}"})
    assert any(n["id"] == notif_id for n in res_hod.get_json())


# ============================================================================
# 4. FRONTEND WIRING VERIFICATION
# ============================================================================

def test_frontend_absence_elements_and_handlers():
    """Verify faculty.html and admin.html contain absence notification UI and hooks."""
    with open(_resolve_file("faculty.html"), "r", encoding="utf-8") as f:
        f_html = f.read()

    # Form inputs and IDs
    assert 'id="f-absence-date"' in f_html
    assert 'id="f-absence-category"' in f_html
    assert 'id="f-absence-reason"' in f_html
    assert 'id="btn-submit-absence"' in f_html
    assert 'handleFacultyAbsenceNotice(event)' in f_html
    assert '/api/notifications/absence' in f_html

    with open(_resolve_file("admin.html"), "r", encoding="utf-8") as f:
        a_html = f.read()

    # Admin elements and functions
    assert 'id="admin-dashboard-notifications-container"' in a_html
    assert 'id="admin-notifications-container"' in a_html
    assert 'renderAdminNotifications()' in a_html
    assert 'Teacher Absence Notice' in a_html
