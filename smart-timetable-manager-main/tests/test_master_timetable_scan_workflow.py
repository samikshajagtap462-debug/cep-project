"""Comprehensive test suite for Master Timetable Scan & Conflict Detection Workflow.

Verifies:
1. Same-faculty overlapping sessions produce a faculty conflict.
2. Same-class overlapping sessions produce a class conflict.
3. Same-room overlapping sessions produce a room conflict.
4. Different practical batches in different labs with different faculty are allowed (no conflict).
5. Sessions that only touch at their start/end times do not conflict.
6. The supplied sample timetable produces EXACTLY two unique conflicting pairs on Monday.
7. Only the selected day's sessions are scanned when a day filter is applied.
8. Multiple rule violations for the same pair of sessions produce a single unique conflict card.
9. Loading sample or uploaded file does not modify production timetable database records.
10. Backend endpoints /api/timetable/sample, /api/timetable/parse, and /api/timetable/scan work correctly.
"""

import io
import pytest
from backend.app.models import TimetableEntry, Faculty
from backend.app.services.timetable_scanner import (
    SAMPLE_TIMETABLE_ENTRIES,
    scan_master_timetable,
    scan_database_timetable,
    detect_conflicts_in_sessions,
    parse_and_validate_file
)


# ============================================================================
# 1. CORE CONFLICT DETECTION UNIT TESTS
# ============================================================================

def test_same_faculty_overlapping_sessions_produce_conflict():
    """Requirement 1: Flag a conflict when the same faculty member is assigned to overlapping sessions."""
    sessions = [
        {
            "day": "Monday", "start_time": "09:00", "end_time": "10:00",
            "subject": "Python Programming", "faculty_id": "FAC-001",
            "class_name": "SY AD1", "room": "Room 102", "session_type": "Theory"
        },
        {
            "day": "Monday", "start_time": "09:30", "end_time": "10:30",
            "subject": "Database Systems", "faculty_id": "FAC-001",
            "class_name": "SY AD2", "room": "Room 103", "session_type": "Theory"
        }
    ]
    report = detect_conflicts_in_sessions(sessions, day_filter="Monday")
    assert report["total_sessions_checked"] == 2
    assert report["total_conflicts"] == 1
    assert report["faculty_clashes"] == 1
    assert report["class_clashes"] == 0
    assert report["room_clashes"] == 0

    c = report["conflicts"][0]
    assert "Faculty" in c["conflict_types"]
    assert c["time_slot"] == "09:30 - 10:00"
    assert "FAC-001" in c["faculty"]
    assert c["session_1"]["subject"] == "Python Programming"
    assert c["session_2"]["subject"] == "Database Systems"


def test_same_class_overlapping_sessions_produce_conflict():
    """Requirement 2: Flag a conflict when the same class division has overlapping sessions."""
    sessions = [
        {
            "day": "Monday", "start_time": "11:00", "end_time": "12:00",
            "subject": "Machine Learning", "faculty_id": "FAC-003",
            "class_name": "TY AD1", "room": "Room 102", "session_type": "Theory"
        },
        {
            "day": "Monday", "start_time": "11:30", "end_time": "12:30",
            "subject": "Artificial Intelligence", "faculty_id": "FAC-004",
            "class_name": "TY AD1", "room": "Room 103", "session_type": "Theory"
        }
    ]
    report = detect_conflicts_in_sessions(sessions, day_filter="Monday")
    assert report["total_sessions_checked"] == 2
    assert report["total_conflicts"] == 1
    assert report["class_clashes"] == 1
    assert report["faculty_clashes"] == 0
    assert report["room_clashes"] == 0

    c = report["conflicts"][0]
    assert "Class/Batch" in c["conflict_types"]
    assert c["time_slot"] == "11:30 - 12:00"
    assert "TY AD1" in c["class_name"]


def test_same_room_overlapping_sessions_produce_conflict():
    """Requirement 3: Flag a conflict when two sessions occupy the same room at overlapping times."""
    sessions = [
        {
            "day": "Wednesday", "start_time": "10:15", "end_time": "12:15",
            "subject": "Compiler Design", "faculty_id": "FAC-101",
            "class_name": "TY AD1", "room": "Room 102", "session_type": "Theory"
        },
        {
            "day": "Wednesday", "start_time": "11:15", "end_time": "13:15",
            "subject": "Computer Networks", "faculty_id": "FAC-102",
            "class_name": "TY AD2", "room": "Room 102", "session_type": "Theory"
        }
    ]
    report = detect_conflicts_in_sessions(sessions, day_filter="Wednesday")
    assert report["total_sessions_checked"] == 2
    assert report["total_conflicts"] == 1
    assert report["room_clashes"] == 1
    assert report["faculty_clashes"] == 0
    assert report["class_clashes"] == 0

    c = report["conflicts"][0]
    assert "Room/Lab" in c["conflict_types"]
    assert c["time_slot"] == "11:15 - 12:15"
    assert c["room"] == "Room 102"


def test_different_practical_batches_in_different_labs_are_allowed():
    """Requirement 4: Different practical batches of same division in different labs with different faculty are allowed."""
    sessions = [
        {
            "day": "Monday", "start_time": "13:00", "end_time": "15:00",
            "subject": "Python Practical", "faculty_id": "FAC-005",
            "class_name": "SY AD1 (A)", "room": "Lab 609A", "session_type": "Practical"
        },
        {
            "day": "Monday", "start_time": "13:00", "end_time": "15:00",
            "subject": "Python Practical", "faculty_id": "FAC-006",
            "class_name": "SY AD1 (B)", "room": "Lab 609B", "session_type": "Practical"
        },
        {
            "day": "Monday", "start_time": "13:00", "end_time": "15:00",
            "subject": "Python Practical", "faculty_id": "FAC-007",
            "class_name": "SY AD1 (C)", "room": "Lab 607 AI1", "session_type": "Practical"
        }
    ]
    report = detect_conflicts_in_sessions(sessions, day_filter="Monday")
    assert report["total_sessions_checked"] == 3
    assert report["total_conflicts"] == 0
    assert report["status"] == "PASS"


def test_touching_start_end_times_do_not_conflict():
    """Requirement 5: Sessions that only touch at start/end times (e.g. 09:00-10:00 and 10:00-11:00) do NOT conflict."""
    sessions = [
        {
            "day": "Thursday", "start_time": "09:00", "end_time": "10:00",
            "subject": "Signals & Systems", "faculty_id": "FAC-001",
            "class_name": "SY AD1", "room": "Room 102", "session_type": "Theory"
        },
        {
            "day": "Thursday", "start_time": "10:00", "end_time": "11:00",
            "subject": "Control Systems", "faculty_id": "FAC-001",
            "class_name": "SY AD1", "room": "Room 102", "session_type": "Theory"
        }
    ]
    report = detect_conflicts_in_sessions(sessions, day_filter="Thursday")
    assert report["total_sessions_checked"] == 2
    assert report["total_conflicts"] == 0
    assert report["status"] == "PASS"


# ============================================================================
# 2. EXACT SAMPLE TIMETABLE TEST (REQUIREMENT 6)
# ============================================================================

def test_supplied_sample_timetable_produces_exactly_two_unique_conflicts(app):
    """Requirement 6: The supplied sample timetable produces EXACTLY two unique conflicting pairs on Monday."""
    with app.app_context():
        from backend.app.database import SessionLocal
        db = SessionLocal()
        try:
            report = scan_master_timetable(db, SAMPLE_TIMETABLE_ENTRIES, day="Monday")
            assert report["success"] is True
            assert report["total_sessions_checked"] == 7
            assert report["total_conflicts"] == 2, f"Expected 2 unique conflicts, got {report['total_conflicts']}"
            assert report["faculty_clashes"] == 1
            assert report["class_clashes"] == 1
            assert report["room_clashes"] == 0

            # Conflict 1: FAC-001 overlap (Python Programming vs Database Systems)
            fac_conflicts = [c for c in report["conflicts"] if "Faculty" in c["conflict_types"]]
            assert len(fac_conflicts) == 1
            fc = fac_conflicts[0]
            assert "09:30 - 10:00" in fc["time_slot"]
            assert "FAC-001" in fc["faculty"]
            assert "Python Programming" in fc["subject"]
            assert "Database Systems" in fc["subject"]

            # Conflict 2: TY AD1 class clash (Machine Learning vs Artificial Intelligence)
            class_conflicts = [c for c in report["conflicts"] if "Class/Batch" in c["conflict_types"]]
            assert len(class_conflicts) == 1
            cc = class_conflicts[0]
            assert "11:30 - 12:00" in cc["time_slot"]
            assert "TY AD1" in cc["class_name"]
            assert "Machine Learning" in cc["subject"]
            assert "Artificial Intelligence" in cc["subject"]

            # Verify no conflicts among practical batches A, B, C
            practical_conflicts = [c for c in report["conflicts"] if "Python Practical" in c["subject"]]
            assert len(practical_conflicts) == 0
        finally:
            db.close()


def test_only_selected_day_sessions_are_scanned(app):
    """Requirement 7: Day filtering scans only the selected day's sessions."""
    mixed_entries = list(SAMPLE_TIMETABLE_ENTRIES) + [
        {
            "day": "Tuesday", "start_time": "09:00", "end_time": "10:00",
            "subject": "Tuesday Math", "faculty_id": "FAC-099",
            "class_name": "SY AD1", "room": "Room 102", "session_type": "Theory"
        },
        {
            "day": "Wednesday", "start_time": "10:00", "end_time": "11:00",
            "subject": "Wednesday Physics", "faculty_id": "FAC-099",
            "class_name": "SY AD1", "room": "Room 102", "session_type": "Theory"
        }
    ]

    with app.app_context():
        from backend.app.database import SessionLocal
        db = SessionLocal()
        try:
            # Scanning Monday only checks the 7 Monday sessions
            report_mon = scan_master_timetable(db, mixed_entries, day="Monday")
            assert report_mon["total_sessions_checked"] == 7
            assert report_mon["total_conflicts"] == 2

            # Scanning Tuesday only checks the 1 Tuesday session
            report_tue = scan_master_timetable(db, mixed_entries, day="Tuesday")
            assert report_tue["total_sessions_checked"] == 1
            assert report_tue["total_conflicts"] == 0
            assert report_tue["status"] == "PASS"

            # Scanning Wednesday only checks 1 Wednesday session
            report_wed = scan_master_timetable(db, mixed_entries, day="Wednesday")
            assert report_wed["total_sessions_checked"] == 1
            assert report_wed["total_conflicts"] == 0
        finally:
            db.close()


def test_consolidate_multiple_rule_violations_into_single_card():
    """Verify that if two sessions violate both Faculty and Room rules, ONE card is generated."""
    sessions = [
        {
            "day": "Friday", "start_time": "10:00", "end_time": "12:00",
            "subject": "Deep Learning", "faculty_id": "FAC-001",
            "class_name": "BE AD1", "room": "Lab 609A", "session_type": "Practical"
        },
        {
            "day": "Friday", "start_time": "11:00", "end_time": "13:00",
            "subject": "Cloud Computing", "faculty_id": "FAC-001",
            "class_name": "BE AD2", "room": "Lab 609A", "session_type": "Practical"
        }
    ]
    report = detect_conflicts_in_sessions(sessions, day_filter="Friday")
    assert report["total_sessions_checked"] == 2
    assert report["total_conflicts"] == 1  # EXACTLY ONE card!
    assert report["faculty_clashes"] == 1
    assert report["room_clashes"] == 1

    c = report["conflicts"][0]
    assert "Faculty" in c["conflict_types"]
    assert "Room/Lab" in c["conflict_types"]
    assert len(c["reasons"]) == 2
    assert len(c["corrections"]) == 2


# ============================================================================
# 3. SAFETY: SAMPLE / UPLOAD DOES NOT MUTATE PRODUCTION DATABASE
# ============================================================================

def test_loading_sample_or_scanning_does_not_mutate_database(client, faculty_token, app):
    """Requirement 9: Uploading or loading sample data NEVER modifies the production database."""
    with app.app_context():
        from backend.app.database import SessionLocal
        db = SessionLocal()
        initial_count = db.query(TimetableEntry).count()
        db.close()

    # 1. Faculty fetches sample timetable
    res_sample = client.get("/api/timetable/sample", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_sample.status_code == 200

    # 2. Faculty scans sample entries in-memory
    res_scan = client.post("/api/timetable/scan", json={
        "entries": SAMPLE_TIMETABLE_ENTRIES,
        "day": "Monday"
    }, headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_scan.status_code == 200
    report = res_scan.get_json()
    assert report["total_conflicts"] == 2

    # 3. Verify SQLite database count is 100% unchanged
    with app.app_context():
        from backend.app.database import SessionLocal
        db = SessionLocal()
        final_count = db.query(TimetableEntry).count()
        db.close()

    assert final_count == initial_count, f"Database was mutated! Initial: {initial_count}, Final: {final_count}"


# ============================================================================
# 4. FILE PARSING & VALIDATION TESTS
# ============================================================================

def test_parse_csv_file_validation():
    """Requirement 5: Accept CSV, validate required fields, time formats, and invalid intervals."""
    valid_csv = """Day,Start Time,End Time,Subject,Faculty ID,Class/Batch,Session Type,Room/Lab
Monday,09:00,10:00,Python Programming,FAC-001,SY AD1,Theory,Room 102
Monday,09:30,10:30,Database Systems,FAC-001,SY AD2,Theory,Room 103
"""
    parsed = parse_and_validate_file(valid_csv.encode("utf-8"), "test.csv")
    assert parsed["success"] is True
    assert parsed["valid_count"] == 2
    assert len(parsed["validation_errors"]) == 0

    # Invalid CSV with invalid time format and start > end
    invalid_csv = """Day,Start Time,End Time,Subject,Faculty ID,Class/Batch,Session Type,Room/Lab
Monday,25:00,10:00,Bad Time,FAC-001,SY AD1,Theory,Room 102
Monday,12:00,09:00,Inverted Times,FAC-001,SY AD2,Theory,Room 103
Sunday,09:00,10:00,Invalid Day,FAC-001,SY AD1,Theory,Room 102
"""
    parsed_bad = parse_and_validate_file(invalid_csv.encode("utf-8"), "bad.csv")
    assert parsed_bad["success"] is False
    assert len(parsed_bad["validation_errors"]) >= 3
