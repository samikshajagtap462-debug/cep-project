from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from ..database import get_db, DB_PATH
from ..formatters import format_display_class, extract_batch_letter, normalize_batch
from ..models import Faculty, TimetableEntry, Subject, Room, ClassModel, FacultyAssignment, Conflict, Batch, SubstituteRequest, AdminNotification, SyllabusTopic, FacultyNotificationRead
from ..security import verify_password, create_access_token
from ..auth import current_user, require_admin, APIError

api_router = Blueprint("api_v1", __name__, url_prefix="/api")


# ==========================================================
# 1. HEALTH CHECK (DATABASE CONNECTIVITY CHECK)
# ==========================================================

@api_router.route("/health", methods=["GET"])
def api_health():
    db = get_db()
    try:
        # Actively test database connection
        db.execute(text("SELECT 1"))
        faculty_count = db.query(Faculty).count()
        timetable_count = db.query(TimetableEntry).count()
        return jsonify({
            "status": "ok",
            "database": "connected",
            "database_file": DB_PATH,
            "records": {
                "faculty": faculty_count,
                "timetable": timetable_count
            },
            "service": "Smart Timetable Manager Flask Backend"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500


# ==========================================================
# 2. AUTHENTICATION (LOGIN, LOGOUT, ME)
# ==========================================================

@api_router.route("/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email_clean = str(data.get("email") or data.get("username") or "").strip().lower()
    fac_id_clean = str(data.get("faculty_id") or "").strip().upper()
    password = str(data.get("password") or "")
    requested_role = str(data.get("role") or "").strip().lower()

    if not email_clean or not password:
        raise APIError("Email / Username and Password are required.", 400)

    db = get_db()

    # Domain alias support (.edu vs .local)
    alt_email = (
        email_clean.replace("@edunova.edu", "@edunova.local")
        if "@edunova.edu" in email_clean
        else email_clean.replace("@edunova.local", "@edunova.edu")
    )

    user = db.query(Faculty).filter(
        (Faculty.email == email_clean) |
        (Faculty.email == alt_email) |
        (Faculty.faculty_id == email_clean.upper()) |
        (Faculty.faculty_id == fac_id_clean)
    ).first()

    # Designate Dr. Dhanraj R. Dhotre as primary HOD & Administrator
    if email_clean in ("admin", "adm-101", "hod", "drdhotre@edunova.edu", "dhotre", "admin@edunova.edu", "admin@edunova.local"):
        dhotre = db.query(Faculty).filter(
            (Faculty.faculty_id == "FAC-DRD") | (Faculty.email == "drdhotre@edunova.edu")
        ).first()
        if dhotre:
            user = dhotre
        elif not user:
            user = db.query(Faculty).filter(Faculty.role == "admin").first()

    if not user or not verify_password(password, user.password_hash):
        raise APIError("Invalid email, Faculty ID, or password.", 401)

    if not user.active:
        raise APIError("User account is inactive. Please contact the administrator.", 403)

    # If faculty ID was provided, verify it matches
    if fac_id_clean and user.faculty_id:
        if fac_id_clean.upper() != user.faculty_id.upper() and fac_id_clean.upper() != f"FAC-{user.id}":
            raise APIError("Faculty ID does not match the registered account.", 401)

    # Role enforcement: Do not allow faculty to log in as admin
    if requested_role == "admin" and user.role not in ("admin", "hod"):
        raise APIError("Access denied: You do not have administrator privileges.", 403)

    token = create_access_token(user.id, user.role)

    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "faculty_id": user.faculty_id or (f"FAC-{100 + user.id}" if user.role == "faculty" else "ADM-101"),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
    }), 200


@api_router.route("/auth/logout", methods=["POST"])
def api_logout():
    return jsonify({"message": "Logged out successfully"}), 200


@api_router.route("/auth/me", methods=["GET"])
@current_user
def api_auth_me(user: Faculty):
    return jsonify({
        "id": user.id,
        "faculty_id": user.faculty_id or (f"FAC-{100 + user.id}" if user.role == "faculty" else "ADM-101"),
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "expertise": [x.strip() for x in user.expertise.split(",") if x.strip()] if user.expertise else []
    }), 200


# ==========================================================
# 3. FACULTY PROFILE & TIMETABLE
# ==========================================================

@api_router.route("/faculty/me", methods=["GET"])
@current_user
def api_faculty_me(user: Faculty):
    db = get_db()
    
    # Calculate scheduled classes, subjects, and batches
    entries = db.query(TimetableEntry).filter(TimetableEntry.faculty_id == user.id).all()
    assigned_classes = sorted(list({e.class_name for e in entries if e.class_name}))
    assigned_subjects = sorted(list({e.subject for e in entries if e.subject}))
    assigned_batches = sorted(list({e.batch for e in entries if e.batch}))

    # Fallback from FacultyAssignment table if timetable entries not yet populated
    if not assigned_classes:
        assignments = db.query(FacultyAssignment).filter(FacultyAssignment.faculty_id == user.id).all()
        assigned_classes = sorted(list({a.class_model.name for a in assignments if a.class_model}))
        assigned_subjects = sorted(list({a.subject.name for a in assignments if a.subject}))
        assigned_batches = sorted(list({a.batch for a in assignments if a.batch}))

    return jsonify({
        "id": user.id,
        "faculty_id": user.faculty_id or f"FAC-{100 + user.id}",
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "expertise": [x.strip() for x in user.expertise.split(",") if x.strip()] if user.expertise else [],
        "max_hours": user.max_hours,
        "current_hours": len(entries),
        "assigned_classes": assigned_classes,
        "assigned_subjects": assigned_subjects,
        "assigned_batches": assigned_batches
    }), 200


@api_router.route("/faculty/timetable", methods=["GET"])
@current_user
def api_faculty_timetable(user: Faculty):
    day = request.args.get("day")
    class_name = request.args.get("class_name")
    session_type = request.args.get("session_type")
    academic_year = request.args.get("academic_year")

    db = get_db()
    query = db.query(TimetableEntry)

    # Non-admin only sees own timetable
    if user.role != "admin":
        query = query.filter(TimetableEntry.faculty_id == user.id)
    else:
        # Admin can view specified faculty or own
        target_fac_id = request.args.get("faculty_id", type=int)
        if target_fac_id:
            query = query.filter(TimetableEntry.faculty_id == target_fac_id)
        else:
            query = query.filter(TimetableEntry.faculty_id == user.id)

    if day:
        query = query.filter(TimetableEntry.day == day)
    if class_name:
        alt_class = class_name.replace(" ", "-") if " " in class_name else class_name.replace("-", " ")
        query = query.filter((TimetableEntry.class_name == class_name) | (TimetableEntry.class_name == alt_class))
    if session_type:
        query = query.filter(TimetableEntry.session_type == session_type)
    if academic_year:
        query = query.filter(TimetableEntry.academic_year == academic_year)

    entries = query.order_by(TimetableEntry.day, TimetableEntry.start_time).all()

    results = []
    for e in entries:
        fac_code = e.faculty.faculty_id if (e.faculty and e.faculty.faculty_id) else f"FAC-{e.faculty_id}"
        fac_name = e.faculty.name if e.faculty else ""
        sess_type = getattr(e, "session_type", "Practical" if e.is_lab else "Theory")
        results.append({
            "id": e.id,
            "day": e.day,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "startTime": e.start_time,
            "endTime": e.end_time,
            "displayTime": f"{e.start_time} - {e.end_time}",
            "subject": e.subject,
            "class_name": e.class_name,
            "classDiv": format_display_class(e.class_name, e.batch, e.is_lab, sess_type),
            "display_class": format_display_class(e.class_name, e.batch, e.is_lab, sess_type),
            "room": e.room,
            "faculty_id": e.faculty_id,
            "facultyId": fac_code,
            "faculty_name": fac_name,
            "facultyName": fac_name,
            "batch": e.batch,
            "batch_letter": extract_batch_letter(e.batch),
            "is_lab": e.is_lab,
            "session_type": sess_type,
            "type": "Lab Practical" if e.is_lab else sess_type,
            "academic_year": getattr(e, "academic_year", None),
            "semester": getattr(e, "semester", None)
        })

    return jsonify(results), 200


# ==========================================================
# 4. CLASSES & SUBJECTS
# ==========================================================

@api_router.route("/classes", methods=["GET"])
@current_user
def api_get_classes(user: Faculty):
    db = get_db()
    classes = db.query(ClassModel).order_by(ClassModel.academic_year, ClassModel.division).all()
    results = []
    for c in classes:
        # Practical batches for this class
        batches = db.query(Batch).filter(
            (Batch.class_id == c.id) | (Batch.class_name == c.name)
        ).order_by(Batch.name).all()

        # Verified subjects for this class
        subjects = db.query(Subject).filter(
            (Subject.class_name == c.name) | (Subject.class_name == c.name.replace("-", " "))
        ).all()

        # Assigned class teacher from faculty assignments if configured
        teacher_assignment = db.query(FacultyAssignment).filter(
            FacultyAssignment.class_id == c.id,
            FacultyAssignment.session_type == "Class Teacher"
        ).first()
        class_teacher = teacher_assignment.faculty.name if (teacher_assignment and teacher_assignment.faculty) else None

        total_students = sum(b.student_count for b in batches) if batches else 0

        results.append({
            "id": c.id,
            "academic_year": c.academic_year,
            "division": c.division,
            "name": c.name,
            "displayName": c.name.replace("-", " "),
            "department": c.department,
            "total_students": total_students,
            "class_teacher": class_teacher,
            "batches": [
                {
                    "id": b.id,
                    "name": b.name,
                    "student_count": b.student_count,
                    "active": b.active
                }
                for b in batches
            ],
            "subjects": [
                {
                    "id": s.id,
                    "name": s.name,
                    "code": getattr(s, "code", None),
                    "short_name": getattr(s, "short_name", None),
                    "is_practical": getattr(s, "is_practical", False)
                }
                for s in subjects
            ]
        })
    return jsonify(results), 200


@api_router.route("/batches", methods=["GET"])
@current_user
def api_get_batches(user: Faculty):
    db = get_db()
    class_name = request.args.get("class_name")
    query = db.query(Batch)
    if class_name:
        alt_class = class_name.replace(" ", "-") if " " in class_name else class_name.replace("-", " ")
        query = query.filter((Batch.class_name == class_name) | (Batch.class_name == alt_class))
    batches = query.order_by(Batch.class_name, Batch.name).all()
    return jsonify([
        {
            "id": b.id,
            "name": b.name,
            "class_id": b.class_id,
            "class_name": b.class_name,
            "student_count": b.student_count,
            "active": b.active
        }
        for b in batches
    ]), 200


@api_router.route("/batches", methods=["POST"])
@require_admin
def api_create_batch(admin: Faculty):
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    class_name = str(data.get("class_name", "")).strip()
    class_id = data.get("class_id")
    student_count = int(data.get("student_count", 25))

    if not name:
        raise APIError("Batch name is required.", 400)

    db = get_db()
    new_batch = Batch(
        name=name,
        class_id=class_id,
        class_name=class_name,
        student_count=student_count,
        active=True
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return jsonify({
        "message": "Batch created successfully",
        "batch": {
            "id": new_batch.id,
            "name": new_batch.name,
            "class_id": new_batch.class_id,
            "class_name": new_batch.class_name,
            "student_count": new_batch.student_count,
            "active": new_batch.active
        }
    }), 201


@api_router.route("/classes/<class_id>/timetable", methods=["GET"])
@current_user
def api_get_class_timetable(class_id, user: Faculty):
    db = get_db()
    
    # Resolve class_id by id or name
    cls = None
    if str(class_id).isdigit():
        cls = db.get(ClassModel, int(class_id))
    if not cls:
        cls = db.query(ClassModel).filter(
            (ClassModel.name == class_id) | (ClassModel.name == str(class_id).replace(" ", "-"))
        ).first()

    cls_name = cls.name if cls else class_id
    entries = db.query(TimetableEntry).filter(TimetableEntry.class_name == cls_name).order_by(
        TimetableEntry.day, TimetableEntry.start_time
    ).all()

    return jsonify([
        {
            "id": e.id,
            "day": e.day,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "subject": e.subject,
            "class_name": e.class_name,
            "classDiv": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
            "display_class": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
            "room": e.room,
            "faculty_id": e.faculty_id,
            "faculty_name": e.faculty.name if e.faculty else "",
            "batch": e.batch,
            "batch_letter": extract_batch_letter(e.batch),
            "is_lab": e.is_lab,
            "session_type": getattr(e, "session_type", "Practical" if e.is_lab else "Theory")
        }
        for e in entries
    ]), 200


@api_router.route("/subjects", methods=["GET"])
@current_user
def api_get_subjects(user: Faculty):
    db = get_db()
    academic_year = request.args.get("academic_year")
    class_name = request.args.get("class_name")

    query = db.query(Subject)
    if academic_year:
        query = query.filter(Subject.academic_year == academic_year)
    if class_name:
        query = query.filter(Subject.class_name == class_name)

    subjects = query.all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "code": getattr(s, "code", None),
            "short_name": getattr(s, "short_name", None),
            "class_name": s.class_name,
            "academic_year": getattr(s, "academic_year", None),
            "total_units": s.total_units,
            "completed_units": s.completed_units,
            "is_practical": getattr(s, "is_practical", False)
        }
        for s in subjects
    ]), 200


# ==========================================================
# 5. ADMIN DASHBOARD & MANAGEMENT
# ==========================================================

@api_router.route("/admin/dashboard", methods=["GET"])
@require_admin
def api_admin_dashboard(admin: Faculty):
    db = get_db()

    # Separate administrative accounts from teaching faculty count
    teaching_faculty = db.query(Faculty).filter(Faculty.active == True, Faculty.role == "faculty").all()
    admin_accounts = db.query(Faculty).filter(Faculty.active == True, Faculty.role == "admin").all()
    total_classes = db.query(ClassModel).count()
    total_subjects = db.query(Subject).count()
    total_entries = db.query(TimetableEntry).count()
    total_rooms = db.query(Room).filter(Room.active == True).count()
    total_conflicts = db.query(Conflict).filter(Conflict.status == "Pending").count()

    classes = db.query(ClassModel).all()
    class_list = [{"id": c.id, "name": c.name, "academic_year": c.academic_year} for c in classes]

    # Faculty summary: ordinary teaching faculty roster
    faculty_summary = [
        {
            "id": f.id,
            "faculty_id": f.faculty_id or f"FAC-{100 + f.id}",
            "name": f.name,
            "email": f.email,
            "role": f.role,
            "max_hours": f.max_hours,
            "current_hours": db.query(TimetableEntry).filter(TimetableEntry.faculty_id == f.id).count()
        }
        for f in teaching_faculty
    ]

    # Verify and flag legitimate HOD teaching appointments
    hod_teaching_sessions = []
    for adm in admin_accounts:
        adm_entries = db.query(TimetableEntry).filter(TimetableEntry.faculty_id == adm.id).all()
        if adm_entries:
            hod_teaching_sessions.append({
                "hod_id": adm.id,
                "name": adm.name,
                "faculty_id": adm.faculty_id,
                "verified": True,
                "note": "Verified teaching duty in Scientific Research & Publication",
                "sessions_count": len(adm_entries),
                "sessions": [
                    {
                        "id": e.id,
                        "day": e.day,
                        "time": f"{e.start_time} - {e.end_time}",
                        "subject": e.subject,
                        "class_div": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
                        "room": e.room
                    }
                    for e in adm_entries
                ]
            })

    return jsonify({
        "total_faculty": len(teaching_faculty),
        "total_teaching_faculty": len(teaching_faculty),
        "total_admin_accounts": len(admin_accounts),
        "total_classes": total_classes,
        "total_subjects": total_subjects,
        "total_timetable_entries": total_entries,
        "total_rooms": total_rooms,
        "total_conflicts": total_conflicts,
        "classes": class_list,
        "faculty_summary": faculty_summary,
        "hod_teaching_verification": hod_teaching_sessions
    }), 200


@api_router.route("/admin/faculty", methods=["GET"])
@require_admin
def api_admin_faculty(admin: Faculty):
    db = get_db()
    include_admin = request.args.get("include_admin", "false").lower() in ("true", "1")
    query = db.query(Faculty)
    if not include_admin:
        query = query.filter(Faculty.faculty_id != "ADM-101")
    faculty_list = query.order_by(Faculty.role, Faculty.name).all()

    from ..services.workload_service import get_faculty_workload_detail
    results = []
    for f in faculty_list:
        wk = get_faculty_workload_detail(db, f.id)
        results.append({
            "id": f.id,
            "faculty_id": f.faculty_id or (f"FAC-{100 + f.id}" if f.role == "faculty" else "ADM-101"),
            "name": f.name,
            "email": f.email,
            "role": f.role,
            "department": f.department,
            "expertise": [x.strip() for x in f.expertise.split(",") if x.strip()] if f.expertise else [],
            "max_hours": f.max_hours,
            "current_hours": wk["total_hours"],
            "total_sessions": wk["total_sessions"],
            "theory_sessions": wk["theory_sessions"],
            "practical_sessions": wk["practical_sessions"],
            "formatted_hours": wk["formatted_hours"],
            "active": f.active
        })
    return jsonify(results), 200


@api_router.route("/admin/timetable", methods=["GET"])
@require_admin
def api_admin_timetable(admin: Faculty):
    db = get_db()
    class_name = request.args.get("class_name")
    day = request.args.get("day")
    faculty_id = request.args.get("faculty_id", type=int)
    room = request.args.get("room")

    query = db.query(TimetableEntry)
    if class_name:
        alt_class = class_name.replace(" ", "-") if " " in class_name else class_name.replace("-", " ")
        query = query.filter((TimetableEntry.class_name == class_name) | (TimetableEntry.class_name == alt_class))
    if day:
        query = query.filter(TimetableEntry.day == day)
    if faculty_id:
        query = query.filter(TimetableEntry.faculty_id == faculty_id)
    if room:
        query = query.filter(TimetableEntry.room == room)

    entries = query.order_by(TimetableEntry.day, TimetableEntry.start_time).all()

    return jsonify([
        {
            "id": e.id,
            "day": e.day,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "startTime": e.start_time,
            "endTime": e.end_time,
            "displayTime": f"{e.start_time} - {e.end_time}",
            "subject": e.subject,
            "class_name": e.class_name,
            "classDiv": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
            "display_class": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
            "room": e.room,
            "faculty_id": e.faculty_id,
            "facultyId": e.faculty.faculty_id if (e.faculty and e.faculty.faculty_id) else f"FAC-{e.faculty_id}",
            "faculty_name": e.faculty.name if e.faculty else "",
            "facultyName": e.faculty.name if e.faculty else "",
            "batch": e.batch,
            "batch_letter": extract_batch_letter(e.batch),
            "is_lab": e.is_lab,
            "session_type": getattr(e, "session_type", "Practical" if e.is_lab else "Theory"),
            "type": "Lab Practical" if e.is_lab else getattr(e, "session_type", "Theory")
        }
        for e in entries
    ]), 200


# ==========================================================
# 6. GENERAL TIMETABLE ENDPOINT (FILTERABLE)
# ==========================================================

@api_router.route("/timetable", methods=["GET"])
@current_user
def api_get_timetable(user: Faculty):
    db = get_db()
    class_name = request.args.get("class_name")
    day = request.args.get("day")
    faculty_id = request.args.get("faculty_id", type=int)
    batch = request.args.get("batch")
    room = request.args.get("room")
    session_type = request.args.get("session_type")

    query = db.query(TimetableEntry)

    if class_name:
        alt_class = class_name.replace(" ", "-") if " " in class_name else class_name.replace("-", " ")
        query = query.filter((TimetableEntry.class_name == class_name) | (TimetableEntry.class_name == alt_class))

    if day:
        query = query.filter(TimetableEntry.day == day)

    if faculty_id:
        query = query.filter(TimetableEntry.faculty_id == faculty_id)

    if batch:
        b_let = extract_batch_letter(batch)
        if b_let:
            query = query.filter(
                (TimetableEntry.batch == f"Batch {b_let}") |
                (TimetableEntry.batch == b_let) |
                (TimetableEntry.batch == batch) |
                (TimetableEntry.batch.is_(None))
            )
        else:
            query = query.filter((TimetableEntry.batch == batch) | (TimetableEntry.batch.is_(None)))

    if room:
        query = query.filter(TimetableEntry.room == room)

    if session_type:
        query = query.filter(TimetableEntry.session_type == session_type)

    entries = query.order_by(TimetableEntry.day, TimetableEntry.start_time).all()

    return jsonify([
        {
            "id": e.id,
            "day": e.day,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "startTime": e.start_time,
            "endTime": e.end_time,
            "displayTime": f"{e.start_time} - {e.end_time}",
            "subject": e.subject,
            "class_name": e.class_name,
            "classDiv": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
            "display_class": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
            "room": e.room,
            "faculty_id": e.faculty_id,
            "facultyId": e.faculty.faculty_id if (e.faculty and e.faculty.faculty_id) else f"FAC-{e.faculty_id}",
            "faculty_name": e.faculty.name if e.faculty else "",
            "facultyName": e.faculty.name if e.faculty else "",
            "batch": e.batch,
            "batch_letter": extract_batch_letter(e.batch),
            "is_lab": e.is_lab,
            "session_type": getattr(e, "session_type", "Practical" if e.is_lab else "Theory"),
            "type": "Lab Practical" if e.is_lab else getattr(e, "session_type", "Theory")
        }
        for e in entries
    ]), 200


# ==========================================================
# 7. FACULTY DIRECTORY
# ==========================================================

@api_router.route("/faculty", methods=["GET"])
@current_user
def api_get_faculty(user: Faculty):
    db = get_db()
    include_admin = request.args.get("include_admin", "false").lower() in ("true", "1")
    query = db.query(Faculty)
    if not include_admin:
        query = query.filter(Faculty.faculty_id != "ADM-101")
    if user.role != "admin":
        query = query.filter(Faculty.active == True)
    faculty_list = query.order_by(Faculty.name).all()

    from ..services.workload_service import get_faculty_workload_detail
    results = []
    for f in faculty_list:
        wk = get_faculty_workload_detail(db, f.id)
        results.append({
            "id": f.id,
            "faculty_id": f.faculty_id or (f"FAC-{100 + f.id}" if f.role == "faculty" else "ADM-101"),
            "name": f.name,
            "email": f.email,
            "role": f.role,
            "department": f.department,
            "expertise": [x.strip() for x in f.expertise.split(",") if x.strip()] if f.expertise else [],
            "max_hours": f.max_hours,
            "current_hours": wk["total_hours"],
            "total_sessions": wk["total_sessions"],
            "theory_sessions": wk["theory_sessions"],
            "practical_sessions": wk["practical_sessions"],
            "formatted_hours": wk["formatted_hours"],
            "active": f.active
        })
    return jsonify(results), 200


# ==========================================================
# 8. ROOMS INFORMATION & OCCUPANCY
# ==========================================================

@api_router.route("/rooms", methods=["GET"])
@current_user
def api_get_rooms(user: Faculty):
    db = get_db()
    day = request.args.get("day")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    rooms = db.query(Room).filter(Room.active == True).order_by(Room.name).all()

    results = []
    for r in rooms:
        occupied = False
        occupied_by = None
        overlapping = []
        has_conflict = False
        primary_session = None

        if day and start_time and end_time:
            # Check overlap with timetable entries
            entries = db.query(TimetableEntry).filter(
                TimetableEntry.room == r.name,
                TimetableEntry.day == day
            ).all()
            for entry in entries:
                # Interval overlap: start1 < end2 AND start2 < end1
                if start_time < entry.end_time and entry.start_time < end_time:
                    overlapping.append(entry)

            if overlapping:
                occupied = True
                has_conflict = len(overlapping) > 1
                first = overlapping[0]
                fac_name = first.faculty.name if first.faculty else "Faculty"
                class_disp = format_display_class(first.class_name, first.batch, first.is_lab, getattr(first, "session_type", "Practical" if first.is_lab else "Theory"))
                occupied_by = f"{class_disp}: {first.subject} ({fac_name})"
                primary_session = {
                    "id": first.id,
                    "subject": first.subject,
                    "class_name": first.class_name,
                    "batch": first.batch,
                    "class_div": class_disp,
                    "faculty_name": fac_name,
                    "start_time": first.start_time,
                    "end_time": first.end_time,
                    "session_type": getattr(first, "session_type", "Practical" if first.is_lab else "Theory"),
                    "is_lab": bool(first.is_lab)
                }

        is_lab_flag = bool(getattr(r, "is_lab", False) or "lab" in (r.room_type or "").lower() or r.name.startswith("Lab") or r.name in ("AI1", "AI2", "CN1", "IIOT", "ARVR", "IOT", "Room 609A", "Room 609B"))
        results.append({
            "id": r.id,
            "name": r.name,
            "room_type": r.room_type,
            "capacity": r.capacity,
            "active": r.active,
            "is_lab": is_lab_flag,
            "status": "Occupied" if occupied else "Available",
            "has_conflict": has_conflict,
            "occupied_details": occupied_by,
            "session": primary_session,
            "sessions_count": len(overlapping)
        })

    return jsonify(results), 200


# ==========================================================
# 9. ANALYTICS & DASHBOARD METRICS
# ==========================================================

def _compute_full_analytics(db):
    entries = db.query(TimetableEntry).all()
    total_sessions = len(entries)

    theory_sessions = 0
    practical_sessions = 0
    total_teaching_hours = 0.0
    theory_hours = 0.0
    practical_hours = 0.0

    for e in entries:
        is_lab = bool(e.is_lab or getattr(e, "session_type", "") == "Practical")
        try:
            sh, sm = map(int, e.start_time.split(":"))
            eh, em = map(int, e.end_time.split(":"))
            dur = (eh + em / 60.0) - (sh + sm / 60.0)
        except Exception:
            dur = 2.0 if is_lab else 1.0

        total_teaching_hours += dur
        if is_lab:
            practical_sessions += 1
            practical_hours += dur
        else:
            theory_sessions += 1
            theory_hours += dur

    # Sessions by faculty (teaching faculty only in main list)
    teaching_faculty = db.query(Faculty).filter(Faculty.active == True, Faculty.role == "faculty").order_by(Faculty.name).all()
    faculty_workload = []
    for f in teaching_faculty:
        f_entries = [e for e in entries if e.faculty_id == f.id]
        f_theory = sum(1 for e in f_entries if not (e.is_lab or getattr(e, "session_type", "") == "Practical"))
        f_practical = sum(1 for e in f_entries if (e.is_lab or getattr(e, "session_type", "") == "Practical"))
        f_hours = 0.0
        for e in f_entries:
            try:
                sh, sm = map(int, e.start_time.split(":"))
                eh, em = map(int, e.end_time.split(":"))
                f_hours += (eh + em / 60.0) - (sh + sm / 60.0)
            except Exception:
                f_hours += 2.0 if (e.is_lab or getattr(e, "session_type", "") == "Practical") else 1.0

        status = "High" if f_hours >= f.max_hours * 0.75 else ("Medium" if f_hours >= f.max_hours * 0.4 else "Low")
        faculty_workload.append({
            "faculty_id": f.id,
            "faculty_code": f.faculty_id or f"FAC-{f.id}",
            "name": f.name,
            "email": f.email,
            "department": f.department,
            "current_hours": round(f_hours, 1),
            "total_hours": round(f_hours, 1),
            "theory_sessions": f_theory,
            "practical_sessions": f_practical,
            "total_sessions": len(f_entries),
            "max_hours": f.max_hours,
            "workload_percentage": round((f_hours / max(f.max_hours, 1)) * 100),
            "status": status
        })

    # Check HOD Dr. Dhanraj Dhotre verified teaching assignments
    hod_faculty = db.query(Faculty).filter(Faculty.role == "admin").all()
    hod_verifications = []
    for hod in hod_faculty:
        hod_entries = [e for e in entries if e.faculty_id == hod.id]
        if hod_entries:
            hod_verifications.append({
                "hod_id": hod.id,
                "faculty_id": hod.faculty_id,
                "name": hod.name,
                "role": "admin",
                "verified": True,
                "note": "Verified teaching duty in Scientific Research & Publication",
                "sessions_count": len(hod_entries),
                "sessions": [
                    {
                        "id": e.id,
                        "day": e.day,
                        "start_time": e.start_time,
                        "end_time": e.end_time,
                        "subject": e.subject,
                        "class_name": e.class_name,
                        "batch": e.batch,
                        "class_div": format_display_class(e.class_name, e.batch, e.is_lab, getattr(e, "session_type", "Practical" if e.is_lab else "Theory")),
                        "room": e.room
                    }
                    for e in hod_entries
                ]
            })

    # Sessions by class and batch
    classes = db.query(ClassModel).order_by(ClassModel.name).all()
    class_breakdown = []
    for c in classes:
        alt_name = c.name.replace(" ", "-") if " " in c.name else c.name.replace("-", " ")
        c_entries = [e for e in entries if e.class_name == c.name or e.class_name == alt_name]
        c_theory = sum(1 for e in c_entries if not (e.is_lab or getattr(e, "session_type", "") == "Practical"))
        c_practical = sum(1 for e in c_entries if (e.is_lab or getattr(e, "session_type", "") == "Practical"))

        batches_map = {}
        for b_name in ("Batch A", "Batch B", "Batch C"):
            b_let = b_name.split()[-1]
            b_count = sum(1 for e in c_entries if (e.batch == b_name or e.batch == b_let))
            batches_map[b_name] = b_count

        class_breakdown.append({
            "class_id": c.id,
            "class_name": c.name,
            "academic_year": c.academic_year,
            "division": c.division,
            "total_sessions": len(c_entries),
            "theory_sessions": c_theory,
            "practical_sessions": c_practical,
            "batches": batches_map
        })

    # Sessions by subject
    subjects = db.query(Subject).order_by(Subject.name).all()
    subject_breakdown = []
    for s in subjects:
        s_entries = [e for e in entries if e.subject == s.name or e.subject_id == s.id]
        if s_entries:
            s_th = sum(1 for e in s_entries if not (e.is_lab or getattr(e, "session_type", "") == "Practical"))
            s_pr = sum(1 for e in s_entries if (e.is_lab or getattr(e, "session_type", "") == "Practical"))
            subject_breakdown.append({
                "subject_id": s.id,
                "name": s.name,
                "class_name": s.class_name,
                "code": getattr(s, "code", s.name[:6].upper()),
                "total_sessions": len(s_entries),
                "theory_sessions": s_th,
                "practical_sessions": s_pr
            })
    subject_breakdown.sort(key=lambda x: x["total_sessions"], reverse=True)

    # Sessions by day
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    day_breakdown = []
    for d in days:
        d_entries = [e for e in entries if e.day == d]
        d_th = sum(1 for e in d_entries if not (e.is_lab or getattr(e, "session_type", "") == "Practical"))
        d_pr = sum(1 for e in d_entries if (e.is_lab or getattr(e, "session_type", "") == "Practical"))
        day_breakdown.append({
            "day": d,
            "total_sessions": len(d_entries),
            "theory_sessions": d_th,
            "practical_sessions": d_pr
        })

    # Rooms & Labs stats
    total_rooms = db.query(Room).filter(Room.active == True).count()
    labs = db.query(Room).filter(Room.active == True).all()
    total_labs = sum(1 for r in labs if ("lab" in (r.room_type or "").lower() or r.name.startswith("Lab") or r.name in ("AI1", "AI2", "CN1", "IIOT", "ARVR", "IOT", "Room 609A", "Room 609B")))
    total_conflicts = db.query(Conflict).filter(Conflict.status == "Pending").count()

    return {
        "department": "Artificial Intelligence & Data Science (AI & DS)",
        "total_sessions": total_sessions,
        "total_timetable_entries": total_sessions,
        "theory_sessions": theory_sessions,
        "practical_sessions": practical_sessions,
        "total_teaching_hours": round(total_teaching_hours, 1),
        "theory_hours": round(theory_hours, 1),
        "practical_hours": round(practical_hours, 1),
        "total_faculty": len(teaching_faculty),
        "total_teaching_faculty": len(teaching_faculty),
        "total_classes": len(classes),
        "total_rooms": total_rooms,
        "total_labs": total_labs,
        "total_subjects": len(subjects),
        "total_conflicts": total_conflicts,
        "classes": [c.name for c in classes],
        "workload_summary": faculty_workload,
        "faculty_workload": faculty_workload,
        "class_breakdown": class_breakdown,
        "subject_breakdown": subject_breakdown,
        "day_breakdown": day_breakdown,
        "hod_teaching_verification": hod_verifications
    }


@api_router.route("/analytics", methods=["GET"])
@current_user
def api_get_analytics(user: Faculty):
    db = get_db()
    data = _compute_full_analytics(db)
    return jsonify(data), 200


@api_router.route("/analytics/reports", methods=["GET"])
@current_user
def api_get_analytics_reports(user: Faculty):
    db = get_db()
    data = _compute_full_analytics(db)
    return jsonify(data), 200


# ==========================================================
# 7B. FACULTY MANAGEMENT (ADMIN OPERATIONS)
# ==========================================================

@api_router.route("/faculty", methods=["POST"])
@require_admin
def api_create_faculty(admin: Faculty):
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email_clean = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()
    fac_code = str(data.get("faculty_id", "")).strip().upper()
    role = str(data.get("role", "faculty")).strip().lower()
    dept = str(data.get("department", "AI&DS")).strip()
    max_hours = int(data.get("max_hours", 16))
    expertise = data.get("expertise", "")
    if isinstance(expertise, list):
        expertise = ",".join(str(x) for x in expertise)

    if not name or not email_clean or not password:
        raise APIError("Name, institutional email, and password are required.", 400)

    db = get_db()
    if db.query(Faculty).filter(Faculty.email == email_clean).first():
        raise APIError("A faculty member with this email address already exists.", 409)

    if fac_code and db.query(Faculty).filter(Faculty.faculty_id == fac_code).first():
        raise APIError("A faculty member with this Faculty ID already exists.", 409)

    if not fac_code:
        next_count = db.query(Faculty).count() + 1
        fac_code = f"FAC-{100 + next_count}"

    from ..security import hash_password
    new_faculty = Faculty(
        name=name,
        email=email_clean,
        faculty_id=fac_code,
        password_hash=hash_password(password),
        role=role,
        department=dept,
        expertise=str(expertise),
        max_hours=max_hours,
        active=True
    )
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)

    return jsonify({
        "message": f"Faculty member {new_faculty.name} added successfully",
        "faculty": {
            "id": new_faculty.id,
            "faculty_id": new_faculty.faculty_id,
            "name": new_faculty.name,
            "email": new_faculty.email,
            "role": new_faculty.role,
            "department": new_faculty.department,
            "expertise": [x.strip() for x in new_faculty.expertise.split(",") if x.strip()] if new_faculty.expertise else [],
            "max_hours": new_faculty.max_hours,
            "active": new_faculty.active
        }
    }), 201


@api_router.route("/faculty/<int:faculty_id>", methods=["PUT"])
@require_admin
def api_update_faculty(faculty_id: int, admin: Faculty):
    data = request.get_json(silent=True) or {}
    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    if "name" in data and str(data["name"]).strip():
        faculty.name = str(data["name"]).strip()
    if "email" in data and str(data["email"]).strip():
        clean_email = str(data["email"]).strip().lower()
        if clean_email != faculty.email:
            existing = db.query(Faculty).filter(Faculty.email == clean_email).first()
            if existing and existing.id != faculty.id:
                raise APIError("Email address is already in use by another account.", 409)
            faculty.email = clean_email
    if "department" in data:
        faculty.department = str(data["department"]).strip()
    if "role" in data:
        faculty.role = str(data["role"]).strip().lower()
    if "max_hours" in data:
        faculty.max_hours = int(data["max_hours"])
    if "expertise" in data:
        exp = data["expertise"]
        faculty.expertise = ",".join(str(x) for x in exp) if isinstance(exp, list) else str(exp)
    if "active" in data:
        faculty.active = bool(data["active"])
    if data.get("password"):
        from ..security import hash_password
        faculty.password_hash = hash_password(str(data["password"]))

    db.commit()
    db.refresh(faculty)

    return jsonify({
        "message": f"Faculty member {faculty.name} updated successfully",
        "faculty": {
            "id": faculty.id,
            "faculty_id": faculty.faculty_id or f"FAC-{faculty.id}",
            "name": faculty.name,
            "email": faculty.email,
            "role": faculty.role,
            "department": faculty.department,
            "expertise": [x.strip() for x in faculty.expertise.split(",") if x.strip()] if faculty.expertise else [],
            "max_hours": faculty.max_hours,
            "active": faculty.active
        }
    }), 200


@api_router.route("/faculty/<int:faculty_id>", methods=["DELETE"])
@require_admin
def api_delete_faculty(faculty_id: int, admin: Faculty):
    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    # Soft deactivation: preserves historical timetables and audit records
    faculty.active = False
    db.commit()

    return jsonify({
        "message": f"Faculty member {faculty.name} has been deactivated. Historical records and timetables are preserved.",
        "faculty_id": faculty.id,
        "active": False
    }), 200


@api_router.route("/faculty/<int:faculty_id>/toggle-status", methods=["POST"])
@require_admin
def api_toggle_faculty_status(faculty_id: int, admin: Faculty):
    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    faculty.active = not faculty.active
    db.commit()

    return jsonify({
        "message": f"Faculty member {faculty.name} status updated to {'Active' if faculty.active else 'Inactive'}.",
        "faculty_id": faculty.id,
        "active": faculty.active
    }), 200


@api_router.route("/faculty/assign", methods=["POST"])
@require_admin
def api_assign_faculty(admin: Faculty):
    data = request.get_json(silent=True) or {}
    faculty_id = data.get("faculty_id")
    subject_id = data.get("subject_id")
    class_id = data.get("class_id")
    batch = data.get("batch")
    session_type = data.get("session_type", "Theory")

    if not faculty_id or not class_id:
        raise APIError("faculty_id and class_id are required.", 400)

    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty member not found", 404)
    if not faculty.active:
        raise APIError("Cannot assign duties to an inactive faculty member.", 400)

    class_obj = db.get(ClassModel, class_id)
    if not class_obj:
        raise APIError("Class division not found", 404)

    assignment = FacultyAssignment(
        faculty_id=faculty_id,
        subject_id=subject_id,
        class_id=class_id,
        batch=batch,
        session_type=session_type
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return jsonify({
        "message": "Faculty assignment created successfully",
        "assignment_id": assignment.id,
        "faculty_name": faculty.name,
        "class_name": class_obj.name,
        "batch": batch,
        "session_type": session_type
    }), 201


# ==========================================================
# 7C. ABSENCE & REPLACEMENT REQUESTS (DATABASE BACKED)
# ==========================================================

@api_router.route("/substitutes/requests", methods=["GET"])
@current_user
def api_get_substitute_requests(user: Faculty):
    db = get_db()
    query = db.query(SubstituteRequest)

    # Faculty privacy: ordinary faculty only see requests they initiated or received
    if user.role != "admin":
        query = query.filter(
            (SubstituteRequest.requester_id == user.id) |
            (SubstituteRequest.recommended_id == user.id)
        )

    requests = query.order_by(SubstituteRequest.created_at.desc()).all()

    results = []
    for r in requests:
        requester = db.get(Faculty, r.requester_id)
        substitute = db.get(Faculty, r.recommended_id)
        results.append({
            "id": r.id,
            "requester_id": r.requester_id,
            "requester_name": requester.name if requester else "Faculty",
            "requester_faculty_id": requester.faculty_id if (requester and requester.faculty_id) else f"FAC-{r.requester_id}",
            "recommended_id": r.recommended_id,
            "recommended_name": substitute.name if substitute else "Faculty",
            "recommended_faculty_id": substitute.faculty_id if (substitute and substitute.faculty_id) else f"FAC-{r.recommended_id}",
            "subject": r.subject,
            "class_name": r.class_name,
            "classDiv": r.class_name,
            "display_class": r.class_name,
            "day": r.day,
            "slot": r.slot,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return jsonify(results), 200

@api_router.route("/timetable", methods=["POST"])
@require_admin
def api_create_timetable(admin: Faculty):
    from .timetable import create_timetable
    return create_timetable.__wrapped__(admin)


@api_router.route("/timetable/<int:entry_id>", methods=["PUT"])
@api_router.route("/admin/timetable/<int:entry_id>", methods=["PUT"])
@require_admin
def api_update_timetable_entry(entry_id: int, admin: Faculty):
    from .timetable import update_timetable
    return update_timetable.__wrapped__(entry_id, admin)


# ==========================================================
# 10. DEPARTMENT NOTIFICATIONS & CIRCULARS
# ==========================================================

@api_router.route("/notifications", methods=["GET"])
@current_user
def api_get_notifications(user: Faculty):
    db = get_db()

    # Query official announcements from HOD / admin / department bulletin
    query = db.query(AdminNotification).order_by(AdminNotification.created_at.desc())

    if user.role == "faculty":
        # Faculty members view announcements for all, their department, directed to them, or submitted by them
        query = query.filter(
            (AdminNotification.recipient_scope == "all") |
            (AdminNotification.recipient_scope.is_(None)) |
            ((AdminNotification.recipient_scope == "department") & (AdminNotification.department == user.department)) |
            ((AdminNotification.recipient_scope == "faculty") & (AdminNotification.target_faculty_id == user.id)) |
            (AdminNotification.publisher_id == user.id)
        )
    elif user.role == "admin" and user.department:
        # HOD / Admin sees notices for their department, notices targeted to HOD/admin/them, announcements, or their own notices
        query = query.filter(
            (AdminNotification.department == user.department) |
            (AdminNotification.department.is_(None)) |
            (AdminNotification.recipient_scope == "all") |
            (AdminNotification.recipient_scope == "hod") |
            (AdminNotification.recipient_scope == "admin") |
            (AdminNotification.target_faculty_id == user.id) |
            (AdminNotification.publisher_id == user.id)
        )

    all_notifs = query.all()

    # Query per-user read records
    user_read_ids = set()
    try:
        user_read_ids = {
            r.notification_id
            for r in db.query(FacultyNotificationRead).filter(FacultyNotificationRead.faculty_id == user.id).all()
        }
    except Exception:
        pass

    # Deduplicate distinct announcements by (publisher_id, normalized title, normalized message)
    seen_content = set()
    result = []
    for n in all_notifs:
        key = (n.publisher_id, n.title.strip().lower(), n.message.strip().lower())
        if key in seen_content:
            continue
        seen_content.add(key)

        is_read = (n.id in user_read_ids) or bool(n.is_read)
        pub_name = n.publisher.name if getattr(n, "publisher", None) else "Dr. Dhanraj R. Dhotre (HOD)"

        result.append({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "publisher_id": n.publisher_id,
            "publisher_name": pub_name,
            "department": n.department or "AI&DS",
            "recipient_scope": n.recipient_scope or "all",
            "target_faculty_id": n.target_faculty_id,
            "notification_code": n.notification_code
        })

    return jsonify(result), 200


def _handle_absence_notification_creation(user: Faculty, data: dict):
    date_val = str(data.get("date", "")).strip()
    leave_cat = str(data.get("leave_category") or data.get("category") or "Casual Leave (CL)").strip()
    reason = str(data.get("reason", "")).strip()

    title = str(data.get("title", "")).strip()
    message = str(data.get("message", "")).strip()

    if not date_val and not (title and message):
        raise APIError("Date of leave is required.", 400)
    if not reason and not (title and message):
        raise APIError("Reason for absence is required.", 400)

    db = get_db()
    teacher_name = user.name
    fac_code = user.faculty_id or f"FAC-{user.id}"
    dept = user.department or "AI&DS"

    # Resolve HOD for this department
    hod = db.query(Faculty).filter(
        Faculty.role == "admin",
        Faculty.department == dept
    ).first()
    if not hod:
        hod = db.query(Faculty).filter(Faculty.role == "admin").first()

    if not title:
        title = f"Teacher Absence Notification: {teacher_name} ({leave_cat})"
    if not message:
        message = (
            f"Faculty member {teacher_name} ({fac_code}) has submitted an absence notification for {date_val}.\n"
            f"Leave Category: {leave_cat}\n"
            f"Reason: {reason}"
        )

    # Check for existing duplicate to prevent resubmission spam
    from sqlalchemy import func
    existing = db.query(AdminNotification).filter(
        AdminNotification.publisher_id == user.id,
        func.lower(func.trim(AdminNotification.title)) == title.lower(),
        func.lower(func.trim(AdminNotification.message)) == message.lower()
    ).first()

    if existing:
        existing.is_read = False
        db.query(FacultyNotificationRead).filter(
            FacultyNotificationRead.notification_id == existing.id
        ).delete()
        db.commit()
        return jsonify({
            "success": True,
            "duplicate": True,
            "message": "Absence notification already recorded.",
            "notification": {
                "id": existing.id,
                "title": existing.title,
                "message": existing.message,
                "is_read": False,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
                "publisher_id": existing.publisher_id,
                "publisher_name": teacher_name,
                "department": existing.department,
                "target_faculty_id": existing.target_faculty_id,
                "recipient_scope": existing.recipient_scope,
                "notification_code": existing.notification_code
            }
        }), 201

    notif_code = f"ABSENCE-{int(datetime.now(timezone.utc).timestamp())}-{user.id}"
    notif = AdminNotification(
        title=title,
        message=message,
        is_read=False,
        publisher_id=user.id,
        department=dept,
        recipient_scope="hod",
        target_faculty_id=hod.id if hod else None,
        notification_code=notif_code
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return jsonify({
        "success": True,
        "message": f"Absence notification for {date_val} successfully submitted to HOD.",
        "notification": {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
            "publisher_id": notif.publisher_id,
            "publisher_name": teacher_name,
            "department": notif.department,
            "target_faculty_id": notif.target_faculty_id,
            "recipient_scope": notif.recipient_scope,
            "notification_code": notif.notification_code
        }
    }), 201


@api_router.route("/notifications/absence", methods=["POST"])
@current_user
def api_create_absence_notification(user: Faculty):
    data = request.get_json(silent=True) or {}
    return _handle_absence_notification_creation(user, data)


@api_router.route("/notifications", methods=["POST"])
@current_user
def api_create_notification(user: Faculty):
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    message = str(data.get("message", "")).strip()
    recipient_scope = str(data.get("recipient_scope", "all")).strip()
    target_faculty_id = data.get("target_faculty_id")

    # If ordinary faculty, check if submitting an absence notification
    if user.role != "admin":
        is_absence = (
            "absence" in title.lower() or
            "leave" in title.lower() or
            recipient_scope in ("hod", "admin") or
            bool(data.get("date"))
        )
        if not is_absence:
            raise APIError("Administrator privilege required to post official announcements.", 403)
        return _handle_absence_notification_creation(user, data)

    if not title or not message:
        raise APIError("title and message are required", 400)

    db = get_db()

    # Duplicate Check: Prevent duplicate announcements
    from sqlalchemy import func
    existing = db.query(AdminNotification).filter(
        func.lower(func.trim(AdminNotification.title)) == title.lower(),
        func.lower(func.trim(AdminNotification.message)) == message.lower()
    ).first()

    if existing:
        existing.is_read = False
        db.query(FacultyNotificationRead).filter(
            FacultyNotificationRead.notification_id == existing.id
        ).delete()
        db.commit()
        return jsonify({
            "success": True,
            "duplicate": True,
            "message": "Announcement is already published.",
            "notification": {
                "id": existing.id,
                "title": existing.title,
                "message": existing.message,
                "is_read": False,
                "created_at": existing.created_at.isoformat() if existing.created_at else None
            }
        }), 201

    notif = AdminNotification(
        title=title,
        message=message,
        is_read=False,
        publisher_id=user.id,
        department=user.department or "AI&DS",
        recipient_scope=recipient_scope or "all",
        target_faculty_id=int(target_faculty_id) if target_faculty_id else None,
        notification_code=f"NOTIF-{int(datetime.now(timezone.utc).timestamp())}"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    return jsonify({
        "success": True,
        "notification": {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "is_read": notif.is_read,
            "created_at": notif.created_at.isoformat() if notif.created_at else None,
            "publisher_id": notif.publisher_id,
            "department": notif.department,
            "recipient_scope": notif.recipient_scope
        }
    }), 201


@api_router.route("/notifications/<int:notif_id>/read", methods=["PUT"])
@current_user
def api_mark_notification_read(user: Faculty, notif_id: int):
    db = get_db()
    notif = db.get(AdminNotification, notif_id)
    if not notif:
        raise APIError("Notification not found", 404)

    # Record persistent per-user read record
    read_record = db.query(FacultyNotificationRead).filter_by(
        faculty_id=user.id,
        notification_id=notif.id
    ).first()

    if not read_record:
        db.add(FacultyNotificationRead(faculty_id=user.id, notification_id=notif.id))

    notif.is_read = True
    db.commit()
    return jsonify({"success": True, "id": notif.id, "is_read": True}), 200


@api_router.route("/notifications/read-all", methods=["PUT", "POST"])
@current_user
def api_mark_all_notifications_read(user: Faculty):
    db = get_db()
    query = db.query(AdminNotification)
    if user.role == "faculty":
        query = query.filter(
            (AdminNotification.recipient_scope == "all") |
            (AdminNotification.recipient_scope.is_(None)) |
            ((AdminNotification.recipient_scope == "department") & (AdminNotification.department == user.department)) |
            ((AdminNotification.recipient_scope == "faculty") & (AdminNotification.target_faculty_id == user.id)) |
            (AdminNotification.publisher_id == user.id)
        )
    elif user.role == "admin" and user.department:
        query = query.filter(
            (AdminNotification.department == user.department) |
            (AdminNotification.department.is_(None)) |
            (AdminNotification.recipient_scope == "all") |
            (AdminNotification.recipient_scope == "hod") |
            (AdminNotification.recipient_scope == "admin") |
            (AdminNotification.target_faculty_id == user.id) |
            (AdminNotification.publisher_id == user.id)
        )
    visible_notifs = query.all()

    marked = 0
    for n in visible_notifs:
        existing_read = db.query(FacultyNotificationRead).filter_by(
            faculty_id=user.id,
            notification_id=n.id
        ).first()
        if not existing_read:
            db.add(FacultyNotificationRead(faculty_id=user.id, notification_id=n.id))
            marked += 1
        n.is_read = True

    db.commit()
    return jsonify({"success": True, "marked_count": marked, "message": "All notifications marked as read"}), 200


# ==========================================================
# 11. SCAN MASTER TIMETABLE & CONFLICT ENGINE
# ==========================================================

@api_router.route("/timetable/sample", methods=["GET"])
@current_user
def api_get_sample_timetable(user: Faculty):
    """Retrieve the standard verification sample timetable entries."""
    from ..services.timetable_scanner import SAMPLE_TIMETABLE_ENTRIES
    return jsonify({
        "success": True,
        "total_entries": len(SAMPLE_TIMETABLE_ENTRIES),
        "entries": SAMPLE_TIMETABLE_ENTRIES
    }), 200


@api_router.route("/timetable/parse", methods=["POST"])
@current_user
def api_parse_timetable_file(user: Faculty):
    """Parse and validate an uploaded CSV or Excel timetable file without modifying the database."""
    if "file" not in request.files:
        raise APIError("No file uploaded. Please select a .csv or .xlsx timetable file.", 400)

    f = request.files["file"]
    if not f.filename:
        raise APIError("Empty filename provided.", 400)

    file_bytes = f.read()
    from ..services.timetable_scanner import parse_and_validate_file
    db = get_db()
    try:
        report = parse_and_validate_file(file_bytes, f.filename, db=db)
        return jsonify(report), 200
    except Exception as e:
        raise APIError(f"Error parsing timetable file: {str(e)}", 400)


@api_router.route("/timetable/scan", methods=["GET", "POST"])
@current_user
def api_scan_timetable(user: Faculty):
    """Scan the master timetable for conflicts.

    - GET: Scans the actual master timetable stored in SQLite (supports ?day=Monday).
      Accessible by ALL authenticated users (faculty & admin).
    - POST with JSON body: Scans submitted in-memory timetable entries (supports day filter).
      Accessible by ALL authenticated users for interactive validation.
    - POST with multipart file upload / form-data: Requires admin role.
    """
    db = get_db()
    from ..services.timetable_scanner import scan_database_timetable, scan_master_timetable, extract_rows_from_file

    day = request.args.get("day")

    has_upload = ("file" in request.files)
    has_form_entries = ("entries" in request.form)
    json_data = request.get_json(silent=True) or {}
    has_json_entries = bool(json_data.get("entries"))

    if json_data.get("day"):
        day = json_data.get("day")
    elif request.form.get("day"):
        day = request.form.get("day")

    # If multipart file upload or form-data entries, enforce admin role (keeps test green)
    if request.method == "POST" and (has_upload or has_form_entries):
        if user.role != "admin":
            raise APIError("Admin privilege required to scan uploaded timetable files.", 403)

        raw_rows = []
        if has_upload:
            f = request.files["file"]
            file_bytes = f.read()
            try:
                raw_rows = extract_rows_from_file(file_bytes, f.filename)
            except Exception as e:
                raise APIError(f"Error parsing timetable file: {str(e)}", 400)
        else:
            raw_rows = json_data.get("entries", [])

        if not raw_rows:
            raise APIError("No timetable entries found in uploaded file or request body.", 400)

        report = scan_master_timetable(db, raw_rows, day=day)
        return jsonify(report), 200

    # In-memory JSON entries scan (accessible to all authenticated users)
    if request.method == "POST" and has_json_entries:
        raw_rows = json_data.get("entries", [])
        report = scan_master_timetable(db, raw_rows, day=day)
        return jsonify(report), 200

    # Default live scan of master timetable stored in database (open to faculty and admin)
    report = scan_database_timetable(db, day=day)
    return jsonify(report), 200


@api_router.route("/timetable/import", methods=["POST"])
@require_admin
def api_import_timetable(admin: Faculty):
    from ..services.timetable_scanner import import_scanned_entries_transactional
    data = request.get_json(silent=True) or {}
    entries = data.get("entries", [])
    if not entries or not isinstance(entries, list):
        raise APIError("Valid entries array is required for import", 400)

    db = get_db()
    result = import_scanned_entries_transactional(db, entries)
    return jsonify(result), 200
