"""Master Timetable Scanner and Conflict Detection Service.

Provides parsing, validation, conflict detection, and transactional import
for Master Timetable files (.csv, .xlsx).
"""

import io
import csv
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..models import Faculty, Room, ClassModel, Subject, TimetableEntry
from ..formatters import format_display_class, extract_batch_letter, normalize_batch
from .workload_service import calculate_session_duration

VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

CANONICAL_CLASSES = {
    "SY AD1": "SY-AD1", "SY-AD1": "SY-AD1", "SYAD1": "SY-AD1",
    "SY AD2": "SY-AD2", "SY-AD2": "SY-AD2", "SYAD2": "SY-AD2",
    "SY AD3": "SY-AD3", "SY-AD3": "SY-AD3", "SYAD3": "SY-AD3",
    "TY AD1": "TY-AD1", "TY-AD1": "TY-AD1", "TYAD1": "TY-AD1",
    "TY AD2": "TY-AD2", "TY-AD2": "TY-AD2", "TYAD2": "TY-AD2",
    "BE AD1": "BE-AD1", "BE-AD1": "BE-AD1", "BEAD1": "BE-AD1",
    "BE AD2": "BE-AD2", "BE-AD2": "BE-AD2", "BEAD2": "BE-AD2"
}

# The canonical sample timetable specified in system requirements
SAMPLE_TIMETABLE_ENTRIES = [
    {
        "day": "Monday",
        "start_time": "09:00",
        "end_time": "10:00",
        "subject": "Python Programming",
        "faculty_id": "FAC-001",
        "class_name": "SY AD1",
        "session_type": "Theory",
        "room": "Room 102"
    },
    {
        "day": "Monday",
        "start_time": "09:30",
        "end_time": "10:30",
        "subject": "Database Systems",
        "faculty_id": "FAC-001",
        "class_name": "SY AD2",
        "session_type": "Theory",
        "room": "Room 103"
    },
    {
        "day": "Monday",
        "start_time": "11:00",
        "end_time": "12:00",
        "subject": "Machine Learning",
        "faculty_id": "FAC-003",
        "class_name": "TY AD1",
        "session_type": "Theory",
        "room": "Room 102"
    },
    {
        "day": "Monday",
        "start_time": "11:30",
        "end_time": "12:30",
        "subject": "Artificial Intelligence",
        "faculty_id": "FAC-004",
        "class_name": "TY AD1",
        "session_type": "Theory",
        "room": "Room 103"
    },
    {
        "day": "Monday",
        "start_time": "13:00",
        "end_time": "15:00",
        "subject": "Python Practical",
        "faculty_id": "FAC-005",
        "class_name": "SY AD1 (A)",
        "session_type": "Practical",
        "room": "Lab 609A"
    },
    {
        "day": "Monday",
        "start_time": "13:00",
        "end_time": "15:00",
        "subject": "Python Practical",
        "faculty_id": "FAC-006",
        "class_name": "SY AD1 (B)",
        "session_type": "Practical",
        "room": "Lab 609B"
    },
    {
        "day": "Monday",
        "start_time": "13:00",
        "end_time": "15:00",
        "subject": "Python Practical",
        "faculty_id": "FAC-007",
        "class_name": "SY AD1 (C)",
        "session_type": "Practical",
        "room": "Lab 607 AI1"
    }
]


def normalize_time_str(time_str: str) -> str:
    """Normalize time string to standard HH:MM format."""
    if not time_str:
        return ""
    s = str(time_str).strip()
    # Check if format is H:MM or HH:MM
    m = re.match(r'^(\d{1,2}):(\d{2})$', s)
    if m:
        h, mn = int(m.group(1)), int(m.group(2))
        return f"{h:02d}:{mn:02d}"
    return s


def parse_time_slot(time_str: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse time slot string into (start_time, end_time) formatted as HH:MM."""
    if not time_str:
        return None, None
    s = str(time_str).strip().replace(" to ", "-").replace(" TO ", "-").replace("–", "-")
    parts = s.split("-")
    if len(parts) == 2:
        start = normalize_time_str(parts[0].strip())
        end = normalize_time_str(parts[1].strip())
        return start, end
    return None, None


def extract_rows_from_file(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Extract raw rows from CSV or Excel file bytes."""
    fn = filename.lower()
    raw_rows = []

    if fn.endswith(".csv"):
        text = file_bytes.decode("utf-8-sig", errors="replace")
        reader = csv.reader(io.StringIO(text))
        header = None
        for row in reader:
            if not row or not any(str(x).strip() for x in row):
                continue
            if header is None:
                header = [h.strip().lower() for h in row]
                continue
            row_dict = {}
            for idx, val in enumerate(row):
                if idx < len(header):
                    row_dict[header[idx]] = val.strip()
            raw_rows.append(row_dict)

    elif fn.endswith((".xlsx", ".xls")):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
            sheet = wb.active
            header = None
            for row in sheet.iter_rows(values_only=True):
                if not row or not any(x is not None and str(x).strip() for x in row):
                    continue
                if header is None:
                    header = [str(h).strip().lower() if h is not None else f"col_{i}" for i, h in enumerate(row)]
                    continue
                row_dict = {}
                for idx, val in enumerate(row):
                    if idx < len(header):
                        row_dict[header[idx]] = str(val).strip() if val is not None else ""
                raw_rows.append(row_dict)
        except ImportError:
            raise ValueError("openpyxl library is required to parse Excel files.")
    else:
        raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")

    return raw_rows


def normalize_row_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map flexible column headers to canonical timetable fields."""
    day_val = raw.get("day", raw.get("weekday", ""))
    slot_val = raw.get("time", raw.get("slot", raw.get("time_slot", raw.get("time slot", ""))))
    start_val = raw.get("start_time", raw.get("start time", raw.get("start", "")))
    end_val = raw.get("end_time", raw.get("end time", raw.get("end", "")))

    if not (start_val and end_val) and slot_val:
        start_val, end_val = parse_time_slot(slot_val)

    start_norm = normalize_time_str(str(start_val)) if start_val else ""
    end_norm = normalize_time_str(str(end_val)) if end_val else ""

    subject_val = raw.get("subject", raw.get("course", raw.get("subject_name", raw.get("subject name", ""))))
    class_val = raw.get("class/batch", raw.get("class", raw.get("division", raw.get("class_name", raw.get("class name", raw.get("cohort", ""))))))
    faculty_val = raw.get("faculty id", raw.get("faculty_id", raw.get("faculty", raw.get("teacher", raw.get("instructor", raw.get("faculty_name", ""))))))
    room_val = raw.get("room/lab", raw.get("room", raw.get("lab", raw.get("classroom", raw.get("facility", "")))))
    batch_val = raw.get("batch", raw.get("practical_batch", raw.get("practical batch", "")))
    type_val = raw.get("session type", raw.get("session_type", raw.get("type", raw.get("session", ""))))

    return {
        "day": str(day_val).strip().capitalize(),
        "start_time": start_norm,
        "end_time": end_norm,
        "subject": str(subject_val).strip(),
        "class_name": str(class_val).strip(),
        "faculty": str(faculty_val).strip(),
        "room": str(room_val).strip(),
        "batch": str(batch_val).strip() if batch_val else None,
        "session_type": str(type_val).strip() if type_val else ""
    }


def parse_class_and_batch(raw_class: str, raw_type: str = "", raw_batch: Optional[str] = None) -> Tuple[str, Optional[str], bool]:
    """Extract canonical class division, batch letter (A/B/C), and whether session is a laboratory practical.

    Handles formats such as:
    - 'SY AD1 (A)' -> ('SY AD1', 'A', True)
    - 'SY-AD1' -> ('SY AD1', None, False)
    - 'TY AD1' with type='Practical' -> ('TY AD1', None, True)
    """
    s = str(raw_class or "").strip()
    batch = None

    if raw_batch:
        b_clean = str(raw_batch).upper()
        for letter in ["A", "B", "C"]:
            if letter in b_clean:
                batch = letter
                break

    # Look for (A), (B), (C) or [A], [B], [C]
    m_bracket = re.search(r'[\(\[\{]\s*([A-C])\s*[\)\]\}]', s, re.I)
    if m_bracket:
        batch = m_bracket.group(1).upper()
        s = re.sub(r'[\(\[\{]\s*[A-C]\s*[\)\]\}]', '', s, flags=re.I).strip()
    else:
        # Check for 'Batch A', 'Batch B', 'Batch C'
        for letter in ["A", "B", "C"]:
            if re.search(rf'\bbatch\s*{letter}\b', s, re.I):
                batch = letter
                s = re.sub(rf'\bbatch\s*{letter}\b', '', s, flags=re.I).strip()
                break

    # Clean up base class division
    clean_base = re.sub(r'\s+', ' ', s.replace('-', ' ')).strip().upper()
    if clean_base in CANONICAL_CLASSES:
        clean_base = CANONICAL_CLASSES[clean_base].replace('-', ' ')

    # Determine whether it is a practical session
    t_clean = str(raw_type or "").strip().lower()
    is_lab = (t_clean == "practical") or (batch is not None)

    return clean_base, batch, is_lab


def intervals_overlap(s1: str, e1: str, s2: str, e2: str) -> bool:
    """Check half-open time interval overlap: s1 < e2 AND s2 < e1.

    Adjacent sessions touching at endpoints (e.g., 09:00-10:00 and 10:00-11:00)
    do NOT conflict.
    """
    if not (s1 and e1 and s2 and e2):
        return False
    return s1 < e2 and s2 < e1


def validate_timetable_entry(norm: Dict[str, Any], row_idx: int) -> List[Dict[str, Any]]:
    """Validate required fields, time formats, and intervals for a single row."""
    errors = []

    # 1. Day validation
    if not norm["day"]:
        errors.append({"row": row_idx, "field": "Day", "message": "Day is required."})
    elif norm["day"] not in VALID_DAYS:
        errors.append({"row": row_idx, "field": "Day", "message": f"Invalid day '{norm['day']}'. Must be Monday through Saturday."})

    # 2. Time validations
    time_fmt = re.compile(r'^([01]?\d|2[0-3]):[0-5]\d$')
    if not norm["start_time"]:
        errors.append({"row": row_idx, "field": "Start Time", "message": "Start Time is required."})
    elif not time_fmt.match(norm["start_time"]):
        errors.append({"row": row_idx, "field": "Start Time", "message": f"Invalid start time format '{norm['start_time']}'. Expected HH:MM."})

    if not norm["end_time"]:
        errors.append({"row": row_idx, "field": "End Time", "message": "End Time is required."})
    elif not time_fmt.match(norm["end_time"]):
        errors.append({"row": row_idx, "field": "End Time", "message": f"Invalid end time format '{norm['end_time']}'. Expected HH:MM."})

    if norm["start_time"] and norm["end_time"] and time_fmt.match(norm["start_time"]) and time_fmt.match(norm["end_time"]):
        if norm["start_time"] >= norm["end_time"]:
            errors.append({"row": row_idx, "field": "Time Range", "message": f"Invalid time interval: start ({norm['start_time']}) must be earlier than end ({norm['end_time']})."})

    # 3. Subject validation
    if not norm["subject"]:
        errors.append({"row": row_idx, "field": "Subject", "message": "Subject is required."})

    # 4. Faculty ID validation
    if not norm["faculty"]:
        errors.append({"row": row_idx, "field": "Faculty ID", "message": "Faculty ID is required."})

    # 5. Class validation
    if not norm["class_name"]:
        errors.append({"row": row_idx, "field": "Class/Batch", "message": "Class/Batch is required."})

    # 6. Room validation
    if not norm["room"]:
        errors.append({"row": row_idx, "field": "Room/Lab", "message": "Room/Lab is required."})

    return errors


def parse_and_validate_file(file_bytes: bytes, filename: str, db: Optional[Session] = None) -> Dict[str, Any]:
    """Parse CSV or Excel file, validate columns and fields, and return preview entries."""
    raw_rows = extract_rows_from_file(file_bytes, filename)
    if not raw_rows:
        return {
            "success": False,
            "message": "The uploaded file contains no data rows.",
            "total_rows": 0,
            "valid_count": 0,
            "validation_errors": [{"row": 0, "field": "File", "message": "The uploaded file is empty."}],
            "entries": [],
            "days": []
        }

    validation_errors = []
    normalized_entries = []
    days_set = set()

    for idx, raw in enumerate(raw_rows, start=1):
        norm = normalize_row_data(raw)
        row_errs = validate_timetable_entry(norm, idx)
        if row_errs:
            validation_errors.extend(row_errs)
        else:
            base_class, batch_letter, is_lab = parse_class_and_batch(norm["class_name"], norm["session_type"], norm.get("batch"))
            disp_class = f"{base_class} ({batch_letter})" if (is_lab and batch_letter) else base_class
            stype = "Practical" if is_lab else "Theory"

            entry_dict = {
                "id": idx,
                "row": idx,
                "day": norm["day"],
                "start_time": norm["start_time"],
                "end_time": norm["end_time"],
                "time_slot": f"{norm['start_time']} - {norm['end_time']}",
                "subject": norm["subject"],
                "faculty_id": norm["faculty"],
                "class_name": disp_class,
                "base_class": base_class,
                "batch": batch_letter,
                "is_lab": is_lab,
                "session_type": stype,
                "room": norm["room"]
            }
            normalized_entries.append(entry_dict)
            days_set.add(norm["day"])

    day_order = {d: i for i, d in enumerate(VALID_DAYS)}
    sorted_days = sorted(list(days_set), key=lambda d: day_order.get(d, 99))

    return {
        "success": len(validation_errors) == 0,
        "message": f"Parsed {len(raw_rows)} rows: {len(normalized_entries)} valid entries found." if not validation_errors else f"Found {len(validation_errors)} validation errors across {len(raw_rows)} rows.",
        "total_rows": len(raw_rows),
        "valid_count": len(normalized_entries),
        "validation_errors": validation_errors,
        "entries": normalized_entries,
        "days": sorted_days
    }


def detect_conflicts_in_sessions(sessions: List[Dict[str, Any]], day_filter: Optional[str] = None, db: Optional[Session] = None) -> Dict[str, Any]:
    """Detect scheduling conflicts across a collection of timetable sessions.

    Consolidates multiple rule violations for the same pair of sessions into
    a single unique conflict card with all applicable reasons and suggestions.

    Rules checked:
    1. Same Faculty Conflict (simultaneous overlapping sessions)
    2. Same Room/Lab Conflict (simultaneous double-booking of facility)
    3. Same Class or Practical Batch Conflict:
       - Different practical batches of same division (e.g. SY AD1 (A) and SY AD1 (B))
         in different labs with different faculty are ALLOWED.
       - Same batch double-booked is a CONFLICT.
       - Whole-class theory overlapping with another session is a CONFLICT.
    """
    # 1. Filter by day if requested
    if day_filter and day_filter.strip().lower() != "all":
        target_day = day_filter.strip().capitalize()
        filtered = [s for s in sessions if s.get("day", "").strip().capitalize() == target_day]
    else:
        target_day = "All Days"
        filtered = list(sessions)

    # 2. Build faculty lookup cache if DB available (to display genuine names without inventing)
    faculty_cache = {}
    if db:
        try:
            for f in db.query(Faculty).all():
                if f.faculty_id:
                    faculty_cache[f.faculty_id.strip().upper()] = f.name
                faculty_cache[str(f.id)] = f.name
                if f.name:
                    faculty_cache[f.name.strip().lower()] = f.name
        except Exception:
            pass

    # 3. Sort chronologically for deterministic pairwise scanning
    day_order = {d: i for i, d in enumerate(VALID_DAYS)}
    sorted_sessions = sorted(filtered, key=lambda s: (day_order.get(s.get("day", ""), 99), s.get("start_time", "")))

    conflicts = []
    faculty_clashes = 0
    room_clashes = 0
    class_clashes = 0

    checked_faculty = set()
    checked_rooms = set()
    checked_classes = set()

    for idx, s in enumerate(sorted_sessions):
        if s.get("faculty_id"):
            checked_faculty.add(str(s["faculty_id"]).strip().upper())
        if s.get("room"):
            checked_rooms.add(str(s["room"]).strip().upper())
        if s.get("class_name"):
            checked_classes.add(str(s["class_name"]).strip())

    # 4. Pairwise conflict checking
    n = len(sorted_sessions)
    for i in range(n):
        s1 = sorted_sessions[i]
        c1_base, c1_batch, c1_lab = parse_class_and_batch(s1.get("class_name"), s1.get("session_type"), s1.get("batch"))
        disp1 = f"{c1_base} ({c1_batch})" if (c1_lab and c1_batch) else c1_base

        # Resolve genuine faculty name or fallback to ID
        raw_fac1 = str(s1.get("faculty_id") or s1.get("faculty") or "").strip()
        fac1_key = raw_fac1.upper()
        fac1_name = faculty_cache.get(fac1_key) or faculty_cache.get(raw_fac1.lower()) or raw_fac1
        fac1_display = f"{fac1_name} ({raw_fac1})" if (fac1_name != raw_fac1 and raw_fac1) else fac1_name

        room1 = str(s1.get("room") or "").strip()
        room1_key = room1.lower()

        for j in range(i + 1, n):
            s2 = sorted_sessions[j]

            # Sessions must be on the same day
            if s1.get("day", "").strip().capitalize() != s2.get("day", "").strip().capitalize():
                continue

            # Sessions must overlap in time (half-open: s1 < e2 and s2 < e1)
            if not intervals_overlap(s1["start_time"], s1["end_time"], s2["start_time"], s2["end_time"]):
                continue

            c2_base, c2_batch, c2_lab = parse_class_and_batch(s2.get("class_name"), s2.get("session_type"), s2.get("batch"))
            disp2 = f"{c2_base} ({c2_batch})" if (c2_lab and c2_batch) else c2_base

            raw_fac2 = str(s2.get("faculty_id") or s2.get("faculty") or "").strip()
            fac2_key = raw_fac2.upper()
            fac2_name = faculty_cache.get(fac2_key) or faculty_cache.get(raw_fac2.lower()) or raw_fac2
            fac2_display = f"{fac2_name} ({raw_fac2})" if (fac2_name != raw_fac2 and raw_fac2) else fac2_name

            room2 = str(s2.get("room") or "").strip()
            room2_key = room2.lower()

            violations = []
            reasons = []
            corrections = []

            # -----------------------------------------------------------------
            # A. Same Faculty Conflict
            # -----------------------------------------------------------------
            if fac1_key and fac2_key and fac1_key == fac2_key:
                faculty_clashes += 1
                violations.append("Faculty")
                reasons.append(
                    f"Faculty member {fac1_display} is assigned to two simultaneous sessions: "
                    f"'{s1['subject']}' in {room1} and '{s2['subject']}' in {room2}."
                )
                corrections.append(
                    f"Reassign an available faculty member for '{s2['subject']}' or reschedule one session to a different time slot."
                )

            # -----------------------------------------------------------------
            # B. Room / Lab Conflict
            # -----------------------------------------------------------------
            if room1_key and room2_key and room1_key == room2_key:
                room_clashes += 1
                violations.append("Room/Lab")
                reasons.append(
                    f"Facility {room1} is simultaneously booked for '{s1['subject']}' ({disp1}) and '{s2['subject']}' ({disp2})."
                )
                corrections.append(
                    f"Relocate '{s2['subject']}' to an available alternative classroom or laboratory."
                )

            # -----------------------------------------------------------------
            # C. Class / Practical Batch Conflict
            # -----------------------------------------------------------------
            if c1_base and c2_base and c1_base == c2_base:
                # Both practicals with distinct batches: ALLOWED parallel
                if c1_lab and c2_lab and c1_batch and c2_batch:
                    if c1_batch == c2_batch:
                        class_clashes += 1
                        violations.append("Class/Batch")
                        reasons.append(
                            f"Practical Batch {c1_batch} of class {c1_base} has simultaneous overlapping sessions: "
                            f"'{s1['subject']}' and '{s2['subject']}'."
                        )
                        corrections.append(
                            f"Reschedule Batch {c1_batch} practical for '{s2['subject']}' to an alternative time slot."
                        )
                    else:
                        # Legitimate parallel batches (e.g. Batch A and Batch B in different labs) -> ALLOWED
                        pass
                elif c1_lab and c2_lab and (not c1_batch or not c2_batch):
                    class_clashes += 1
                    violations.append("Class/Batch")
                    reasons.append(
                        f"Class division {c1_base} has overlapping practical sessions without distinct batch assignments."
                    )
                    corrections.append(
                        f"Specify distinct practical batches (e.g. Batch A, Batch B, Batch C) for each parallel lab session."
                    )
                else:
                    # One or both are whole-class theory sessions
                    class_clashes += 1
                    violations.append("Class/Batch")
                    reasons.append(
                        f"Class division {c1_base} has overlapping sessions preventing attendance: "
                        f"'{s1['subject']}' ({disp1}) and '{s2['subject']}' ({disp2})."
                    )
                    corrections.append(
                        f"Reschedule one of the sessions for class {c1_base} to a non-overlapping time period."
                    )

            # -----------------------------------------------------------------
            # Aggregate single unique conflict card for this pair
            # -----------------------------------------------------------------
            if violations:
                overlap_start = max(s1["start_time"], s2["start_time"])
                overlap_end = min(s1["end_time"], s2["end_time"])

                if len(violations) == 1:
                    conflict_type_label = f"{violations[0]} Overlap" if violations[0] == "Faculty" else f"{violations[0]} Conflict"
                else:
                    conflict_type_label = f"{' & '.join(violations)} Conflict"

                s1_id = s1.get("id") or s1.get("row") or f"R{i+1}"
                s2_id = s2.get("id") or s2.get("row") or f"R{j+1}"

                conflicts.append({
                    "id": f"CLASH-{s1_id}-{s2_id}",
                    "conflict_type": conflict_type_label,
                    "row": f"{s1_id} & {s2_id}",
                    "resource": room1 if room1_key == room2_key else (fac1_display if fac1_key == fac2_key else f"{disp1} & {disp2}"),
                    "description": " ".join(reasons),
                    "conflict_types": violations,
                    "severity": "Blocking",
                    "day": s1.get("day", ""),
                    "time_slot": f"{overlap_start} - {overlap_end}",
                    "subject": f"{s1['subject']} / {s2['subject']}",
                    "class_name": f"{disp1} & {disp2}",
                    "faculty": fac1_display if fac1_display == fac2_display else f"{fac1_display} & {fac2_display}",
                    "faculty_id": raw_fac1 if raw_fac1 == raw_fac2 else f"{raw_fac1} & {raw_fac2}",
                    "room": room1 if room1_key == room2_key else f"{room1} & {room2}",
                    "reasons": reasons,
                    "reason": " ".join(reasons),
                    "corrections": corrections,
                    "correction": " ".join(corrections),
                    "session_1": {
                        "id": s1_id,
                        "subject": s1["subject"],
                        "class": disp1,
                        "class_name": c1_base,
                        "batch": c1_batch,
                        "faculty": fac1_display,
                        "faculty_id": raw_fac1,
                        "room": room1,
                        "time": f"{s1['start_time']} - {s1['end_time']}",
                        "session_type": "Practical" if c1_lab else "Theory"
                    },
                    "session_2": {
                        "id": s2_id,
                        "subject": s2["subject"],
                        "class": disp2,
                        "class_name": c2_base,
                        "batch": c2_batch,
                        "faculty": fac2_display,
                        "faculty_id": raw_fac2,
                        "room": room2,
                        "time": f"{s2['start_time']} - {s2['end_time']}",
                        "session_type": "Practical" if c2_lab else "Theory"
                    }
                })

    status = "PASS" if len(conflicts) == 0 else "CONFLICT"
    if status == "PASS":
        message = (
            f"Master Timetable Audit Passed — Zero Conflicts Detected on {target_day}. "
            f"All {len(sorted_sessions)} sessions, batches, faculty, and facilities verified."
        )
    else:
        message = (
            f"Master Timetable Audit: {len(conflicts)} unique conflicting session pairs detected on {target_day} "
            f"({faculty_clashes} faculty, {room_clashes} room, {class_clashes} class/batch)."
        )

    return {
        "success": True,
        "status": status,
        "day_filter": target_day,
        "message": message,
        "total_sessions_checked": len(sorted_sessions),
        "total_conflicts": len(conflicts),
        "faculty_clashes": faculty_clashes,
        "room_clashes": room_clashes,
        "class_clashes": class_clashes,
        "checked_classes_count": len(checked_classes),
        "checked_rooms_count": len(checked_rooms),
        "checked_faculty_count": len(checked_faculty),
        "conflicts": conflicts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def scan_database_timetable(db: Session, day: Optional[str] = None) -> Dict[str, Any]:
    """Scan the live master timetable stored in the SQLite database for scheduling conflicts.

    Supports optional day filtering (e.g. day='Monday' or day='All').
    """
    query = db.query(TimetableEntry)
    if day and day.strip().lower() != "all":
        query = query.filter(TimetableEntry.day == day.strip().capitalize())

    entries = query.all()

    sessions = []
    for e in entries:
        disp_class = format_display_class(e.class_name, e.batch, e.is_lab)
        fac_name = e.faculty.name if e.faculty else f"Faculty #{e.faculty_id}"
        fac_code = e.faculty.faculty_id if (e.faculty and e.faculty.faculty_id) else str(e.faculty_id or "")

        sessions.append({
            "id": e.id,
            "day": e.day,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "time_slot": f"{e.start_time} - {e.end_time}",
            "subject": e.subject,
            "class_name": disp_class,
            "batch": e.batch,
            "is_lab": bool(e.is_lab),
            "session_type": e.session_type or ("Practical" if e.is_lab else "Theory"),
            "faculty_id": fac_code,
            "faculty": fac_name,
            "room": e.room
        })

    report = detect_conflicts_in_sessions(sessions, day_filter=day, db=db)
    return report


def scan_master_timetable(db: Session, raw_rows: List[Dict[str, Any]], day: Optional[str] = None) -> Dict[str, Any]:
    """Normalize raw timetable rows (from CSV/Excel/JSON) and audit them for conflicts."""
    normalized_entries = []
    validation_errors = []

    for idx, r in enumerate(raw_rows, start=1):
        norm = normalize_row_data(r)
        errs = validate_timetable_entry(norm, idx)
        if errs:
            validation_errors.extend(errs)
        else:
            base_class, batch_letter, is_lab = parse_class_and_batch(norm["class_name"], norm["session_type"], norm.get("batch"))
            disp_class = f"{base_class} ({batch_letter})" if (is_lab and batch_letter) else base_class
            stype = "Practical" if is_lab else "Theory"

            normalized_entries.append({
                "id": idx,
                "row": idx,
                "day": norm["day"],
                "start_time": norm["start_time"],
                "end_time": norm["end_time"],
                "time_slot": f"{norm['start_time']} - {norm['end_time']}",
                "subject": norm["subject"],
                "faculty_id": norm["faculty"],
                "class_name": disp_class,
                "base_class": base_class,
                "batch": batch_letter,
                "is_lab": is_lab,
                "session_type": stype,
                "room": norm["room"]
            })

    conflict_report = detect_conflicts_in_sessions(normalized_entries, day_filter=day, db=db)

    # Attach preview and validation metadata
    conflict_report["total_rows"] = len(raw_rows)
    conflict_report["valid_count"] = len(normalized_entries)
    conflict_report["blocking_count"] = len(conflict_report["conflicts"])
    conflict_report["blocking_conflicts"] = conflict_report["conflicts"]
    conflict_report["validation_errors"] = validation_errors
    conflict_report["valid_entries"] = normalized_entries
    conflict_report["can_import"] = (len(conflict_report["conflicts"]) == 0 and len(normalized_entries) > 0 and len(validation_errors) == 0)

    return conflict_report


def import_scanned_entries_transactional(db: Session, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Import valid timetable sessions atomically within a database transaction."""
    imported_records = []
    try:
        faculty_lookup = {f.faculty_id.upper(): f.id for f in db.query(Faculty).all() if f.faculty_id}
        for f in db.query(Faculty).all():
            faculty_lookup[str(f.id)] = f.id

        for item in entries:
            # Map faculty ID to integer primary key if possible
            f_key = str(item.get("faculty_id") or "").strip().upper()
            fac_pk = faculty_lookup.get(f_key, 1)

            entry = TimetableEntry(
                day=item["day"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                subject=item["subject"],
                class_name=item["class_name"],
                room=item["room"],
                faculty_id=fac_pk,
                batch=item.get("batch"),
                is_lab=bool(item.get("is_lab", False)),
                session_type=item.get("session_type", "Practical" if item.get("is_lab") else "Theory")
            )
            db.add(entry)
            imported_records.append(entry)

        db.commit()
        return {
            "success": True,
            "imported_count": len(imported_records),
            "message": f"Successfully imported {len(imported_records)} timetable sessions into the database."
        }
    except Exception as exc:
        db.rollback()
        raise ValueError(f"Transactional import failed: {str(exc)}")
