from flask import Blueprint, request, jsonify

from ..database import get_db
from ..models import Faculty, TimetableEntry
from ..auth import current_user, require_admin, APIError
from ..formatters import format_display_class, extract_batch_letter, normalize_batch

router = Blueprint("timetable", __name__, url_prefix="/timetable")


def time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    return start1 < end2 and start2 < end1


def timetable_response(entry: TimetableEntry) -> dict:
    disp_class = format_display_class(
        entry.class_name,
        entry.batch,
        entry.is_lab,
        getattr(entry, "session_type", "Practical" if entry.is_lab else "Theory")
    )
    b_letter = extract_batch_letter(entry.batch)
    sess_type = getattr(entry, "session_type", "Practical" if entry.is_lab else "Theory")
    return {
        "id": entry.id,
        "day": entry.day,
        "start_time": entry.start_time,
        "end_time": entry.end_time,
        "startTime": entry.start_time,
        "endTime": entry.end_time,
        "displayTime": f"{entry.start_time} - {entry.end_time}",
        "subject": entry.subject,
        "class_name": entry.class_name,
        "classDiv": disp_class,
        "display_class": disp_class,
        "room": entry.room,
        "faculty_id": entry.faculty_id,
        "faculty_name": entry.faculty.name if entry.faculty else "",
        "facultyName": entry.faculty.name if entry.faculty else "",
        "batch": entry.batch,
        "batch_letter": b_letter,
        "is_lab": entry.is_lab,
        "session_type": sess_type,
        "type": "Lab Practical" if entry.is_lab else sess_type,
        "academic_year": getattr(entry, "academic_year", None),
        "semester": getattr(entry, "semester", None)
    }


# ==========================================================
# GET TIMETABLE
# ==========================================================

@router.route("", methods=["GET"])
@current_user
def get_timetable(user: Faculty):
    day = request.args.get("day")
    class_name = request.args.get("class_name")
    faculty_id = request.args.get("faculty_id", type=int)
    batch = request.args.get("batch")
    search = request.args.get("search")

    db = get_db()
    query = db.query(TimetableEntry)

    # Faculty data privacy: faculty members can only view their own timetable
    if user.role == "faculty":
        if faculty_id is not None and faculty_id != user.id:
            raise APIError("Access denied: You can only view your own timetable.", 403)
        query = query.filter(TimetableEntry.faculty_id == user.id)
    else:
        # Admin / HOD access remains unchanged
        if faculty_id is not None:
            query = query.filter(TimetableEntry.faculty_id == faculty_id)

    if day:
        query = query.filter(TimetableEntry.day == day)

    if class_name:
        alt_class = class_name.replace(" ", "-") if " " in class_name else class_name.replace("-", " ")
        query = query.filter((TimetableEntry.class_name == class_name) | (TimetableEntry.class_name == alt_class))

    if batch:
        b_letter = extract_batch_letter(batch)
        if b_letter:
            query = query.filter(
                (TimetableEntry.batch == f"Batch {b_letter}") |
                (TimetableEntry.batch == b_letter) |
                (TimetableEntry.batch == batch)
            )
        else:
            query = query.filter(TimetableEntry.batch == batch)

    entries = query.all()

    if search:
        search_lower = search.lower()
        entries = [
            entry
            for entry in entries
            if (
                search_lower in entry.subject.lower()
                or search_lower in entry.room.lower()
                or (entry.faculty and search_lower in entry.faculty.name.lower())
                or (entry.class_name and search_lower in entry.class_name.lower())
                or (entry.batch and search_lower in entry.batch.lower())
            )
        ]

    return jsonify([timetable_response(entry) for entry in entries]), 200


# ==========================================================
# CLASH DETECTOR (Must precede /<int:entry_id> to avoid route conflict)
# ==========================================================

@router.route("/clashes/check", methods=["GET"])
@current_user
def detect_clashes(user: Faculty):
    db = get_db()
    from ..services.timetable_scanner import scan_database_timetable
    report = scan_database_timetable(db)
    report["total_clashes"] = report["total_conflicts"]
    report["clashes"] = report["conflicts"]
    return jsonify(report), 200


# ==========================================================
# GET SINGLE TIMETABLE ENTRY
# ==========================================================

@router.route("/<int:entry_id>", methods=["GET"])
@current_user
def get_timetable_entry(entry_id: int, user: Faculty):
    db = get_db()
    entry = db.get(TimetableEntry, entry_id)

    if not entry:
        raise APIError("Timetable entry not found", 404)

    # Faculty data privacy: faculty members can only view their own timetable entries
    if user.role == "faculty" and entry.faculty_id != user.id:
        raise APIError(
            "Access denied: You can only view your own timetable entries.",
            403
        )

    return jsonify(timetable_response(entry)), 200


# ==========================================================
# CREATE TIMETABLE ENTRY (ADMIN ONLY)
# ==========================================================

@router.route("", methods=["POST"])
@require_admin
def create_timetable(admin: Faculty):
    data = request.get_json(silent=True) or {}
    db = get_db()

    faculty_id = data.get("faculty_id")
    if faculty_id is None:
        raise APIError("faculty_id is required", 400)

    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    day = data.get("day", "")
    start_time = data.get("start_time", "")
    end_time = data.get("end_time", "")
    room = data.get("room", "")
    class_name = data.get("class_name", "")
    subject = data.get("subject", "")
    is_lab = bool(data.get("is_lab", False)) or data.get("session_type") == "Practical"
    session_type = "Practical" if is_lab else data.get("session_type", "Theory")

    # Batch normalization
    raw_batch = data.get("batch")
    b_letter = extract_batch_letter(raw_batch)
    batch_val = normalize_batch(raw_batch) if b_letter else None

    existing = db.query(TimetableEntry).filter(
        TimetableEntry.day == day
    ).all()

    conflicts = []
    for entry in existing:
        if not time_overlap(start_time, end_time, entry.start_time, entry.end_time):
            continue

        if faculty_id and entry.faculty_id == faculty_id:
            conflicts.append("Faculty is already scheduled")

        if entry.room == room:
            conflicts.append("Room is already occupied")

        if entry.class_name == class_name:
            entry_b_letter = extract_batch_letter(entry.batch)
            # If either session is a full class (theory / no batch) or same batch -> conflict
            if not b_letter or not entry_b_letter or b_letter == entry_b_letter:
                conflicts.append("Class already has another lecture")

    if conflicts:
        raise APIError(
            {
                "message": "Timetable conflict detected",
                "conflicts": list(set(conflicts))
            },
            409
        )

    timetable = TimetableEntry(
        day=day,
        start_time=start_time,
        end_time=end_time,
        subject=subject,
        class_name=class_name,
        room=room,
        faculty_id=faculty_id,
        batch=batch_val,
        is_lab=is_lab,
        session_type=session_type,
        academic_year=data.get("academic_year"),
        semester=data.get("semester")
    )

    db.add(timetable)
    db.commit()
    db.refresh(timetable)

    return jsonify(timetable_response(timetable)), 200


# ==========================================================
# UPDATE TIMETABLE ENTRY (ADMIN ONLY)
# ==========================================================

@router.route("/<int:entry_id>", methods=["PUT"])
@require_admin
def update_timetable(entry_id: int, admin: Faculty):
    data = request.get_json(silent=True) or {}
    db = get_db()

    entry = db.get(TimetableEntry, entry_id)
    if not entry:
        raise APIError("Timetable entry not found", 404)

    day = data.get("day", entry.day)
    start_time = data.get("start_time", entry.start_time)
    end_time = data.get("end_time", entry.end_time)
    room = data.get("room", entry.room)
    class_name = data.get("class_name", entry.class_name)
    subject = data.get("subject", entry.subject)
    faculty_id = data.get("faculty_id", entry.faculty_id)

    faculty = db.get(Faculty, faculty_id) if faculty_id else None
    if faculty_id and not faculty:
        raise APIError("Faculty not found", 404)

    is_lab = bool(data.get("is_lab", entry.is_lab)) if "is_lab" in data else entry.is_lab
    session_type = data.get("session_type", entry.session_type)
    if is_lab and session_type == "Theory":
        session_type = "Practical"

    # Batch normalization
    raw_batch = data.get("batch") if "batch" in data else entry.batch
    b_letter = extract_batch_letter(raw_batch)
    batch_val = normalize_batch(raw_batch) if b_letter else None

    # Check conflicts against other entries excluding this one
    existing = db.query(TimetableEntry).filter(
        TimetableEntry.day == day,
        TimetableEntry.id != entry_id
    ).all()

    conflicts = []
    for other in existing:
        if not time_overlap(start_time, end_time, other.start_time, other.end_time):
            continue

        if faculty_id and other.faculty_id == faculty_id:
            conflicts.append("Faculty is already scheduled")

        if other.room == room:
            conflicts.append("Room is already occupied")

        if other.class_name == class_name:
            other_b_letter = extract_batch_letter(other.batch)
            if not b_letter or not other_b_letter or b_letter == other_b_letter:
                conflicts.append("Class already has another lecture")

    if conflicts:
        raise APIError(
            {
                "message": "Timetable conflict detected",
                "conflicts": list(set(conflicts))
            },
            409
        )

    entry.day = day
    entry.start_time = start_time
    entry.end_time = end_time
    entry.room = room
    entry.class_name = class_name
    entry.subject = subject
    entry.faculty_id = faculty_id
    entry.batch = batch_val
    entry.is_lab = is_lab
    entry.session_type = session_type
    if "academic_year" in data:
        entry.academic_year = data["academic_year"]
    if "semester" in data:
        entry.semester = data["semester"]

    db.commit()
    db.refresh(entry)

    return jsonify(timetable_response(entry)), 200


# ==========================================================
# DELETE TIMETABLE ENTRY (ADMIN ONLY)
# ==========================================================

@router.route("/<int:entry_id>", methods=["DELETE"])
@require_admin
def delete_timetable(entry_id: int, admin: Faculty):
    db = get_db()
    entry = db.get(TimetableEntry, entry_id)

    if not entry:
        raise APIError("Timetable entry not found", 404)

    db.delete(entry)
    db.commit()

    return jsonify({
        "message": "Timetable entry deleted successfully",
        "entry_id": entry_id
    }), 200
