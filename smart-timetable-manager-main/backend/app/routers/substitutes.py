from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Faculty, TimetableEntry, SubstituteRequest
from ..formatters import format_display_class
from ..auth import current_user, APIError

router = Blueprint("substitutes", __name__, url_prefix="/substitutes")


def time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    return start1 < end2 and start2 < end1


def is_faculty_available(
    db: Session,
    faculty_id: int,
    day: str,
    start_time: str,
    end_time: str
) -> bool:
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.faculty_id == faculty_id,
        TimetableEntry.day == day
    ).all()

    for entry in entries:
        if time_overlap(start_time, end_time, entry.start_time, entry.end_time):
            return False

    return True


def get_workload(db: Session, faculty_id: int) -> int:
    return db.query(TimetableEntry).filter(
        TimetableEntry.faculty_id == faculty_id
    ).count()


# ==========================================================
# AI SUBSTITUTE RECOMMENDATION
# ==========================================================

@router.route("/recommend", methods=["GET"])
@current_user
def recommend_substitute(user: Faculty):
    timetable_id = request.args.get("timetable_id", type=int)
    if timetable_id is None:
        raise APIError("timetable_id query parameter is required", 400)

    db = get_db()
    timetable = db.get(TimetableEntry, timetable_id)
    if not timetable:
        raise APIError("Timetable entry not found", 404)

    # Faculty privacy: faculty can only view recommendations for their own lectures
    if user.role == "faculty" and timetable.faculty_id != user.id:
        raise APIError(
            "Access denied: You can only view recommendations for your own scheduled lectures.",
            403
        )

    absent_faculty = db.get(Faculty, timetable.faculty_id)
    if not absent_faculty:
        raise APIError("Faculty not found", 404)

    class_entries = db.query(TimetableEntry).filter(
        TimetableEntry.class_name == timetable.class_name
    ).all()
    class_faculty_ids = {entry.faculty_id for entry in class_entries}

    candidates = db.query(Faculty).filter(
        Faculty.department == absent_faculty.department,
        Faculty.active == True
    ).all()

    recommendations = []
    for faculty in candidates:
        if faculty.id == absent_faculty.id:
            continue

        if faculty.id not in class_faculty_ids:
            continue

        if not is_faculty_available(
            db,
            faculty.id,
            timetable.day,
            timetable.start_time,
            timetable.end_time
        ):
            continue

        workload = get_workload(db, faculty.id)
        if workload >= faculty.max_hours:
            continue

        recommendations.append({
            "faculty_id": faculty.id,
            "faculty_name": faculty.name,
            "department": faculty.department,
            "current_workload": workload,
            "max_hours": faculty.max_hours,
            "available": True,
            "class_name": timetable.class_name,
            "subject": timetable.subject,
            "day": timetable.day,
            "start_time": timetable.start_time,
            "end_time": timetable.end_time
        })

    recommendations.sort(key=lambda x: x["current_workload"])

    return jsonify({
        "message": "Substitute recommendations generated",
        "absent_faculty": absent_faculty.name,
        "department": absent_faculty.department,
        "subject": timetable.subject,
        "class_name": timetable.class_name,
        "day": timetable.day,
        "start_time": timetable.start_time,
        "end_time": timetable.end_time,
        "recommendations": recommendations
    }), 200


# ==========================================================
# FACULTY AVAILABILITY
# ==========================================================

@router.route("/availability", methods=["GET"])
@current_user
def check_faculty_availability(user: Faculty):
    day = request.args.get("day")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if not day or not start_time or not end_time:
        raise APIError("day, start_time, and end_time parameters are required", 400)

    db = get_db()
    faculty_list = db.query(Faculty).filter(
        Faculty.department == user.department,
        Faculty.active == True
    ).all()

    available_faculty = []
    for faculty in faculty_list:
        if is_faculty_available(db, faculty.id, day, start_time, end_time):
            available_faculty.append({
                "faculty_id": faculty.id,
                "faculty_name": faculty.name,
                "department": faculty.department,
                "available": True
            })

    return jsonify({
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "available_faculty": available_faculty
    }), 200


# ==========================================================
# CREATE SUBSTITUTE REQUEST
# ==========================================================

@router.route("/request", methods=["POST"])
@current_user
def create_substitute_request(user: Faculty):
    data = request.get_json(silent=True) or {}
    timetable_id = data.get("timetable_id") or request.args.get("timetable_id", type=int)
    recommended_id = data.get("recommended_id") or request.args.get("recommended_id", type=int)
    reason = data.get("reason", "") or request.args.get("reason", "")

    if not timetable_id or not recommended_id:
        raise APIError("timetable_id and recommended_id are required", 400)

    db = get_db()
    timetable = db.get(TimetableEntry, timetable_id)
    if not timetable:
        raise APIError("Timetable entry not found", 404)

    # Faculty privacy: faculty can only request substitutes for their own scheduled lectures
    if user.role == "faculty" and timetable.faculty_id != user.id:
        raise APIError(
            "Access denied: You can only request substitutes for your own scheduled lectures.",
            403
        )

    recommended = db.query(Faculty).filter(
        Faculty.id == recommended_id,
        Faculty.active == True
    ).first()

    if not recommended:
        raise APIError("Recommended faculty not found", 404)

    disp_class = format_display_class(
        timetable.class_name,
        timetable.batch,
        timetable.is_lab,
        getattr(timetable, "session_type", "Practical" if timetable.is_lab else "Theory")
    )
    req = SubstituteRequest(
        requester_id=user.id,
        recommended_id=recommended_id,
        subject=timetable.subject,
        class_name=disp_class,
        day=timetable.day,
        slot=f"{timetable.start_time}-{timetable.end_time}",
        reason=reason,
        status="Pending"
    )

    db.add(req)
    db.commit()
    db.refresh(req)

    return jsonify({
        "message": "Substitute request created successfully",
        "request_id": req.id,
        "requester": user.name,
        "recommended_faculty": recommended.name,
        "status": req.status
    }), 200


# ==========================================================
# ACCEPT / REJECT SUBSTITUTE REQUEST
# ==========================================================

@router.route("/request/<int:request_id>", methods=["PUT"])
@current_user
def update_substitute_request(request_id: int, user: Faculty):
    data = request.get_json(silent=True) or {}
    status_val = data.get("status") or request.args.get("status")

    if status_val not in ["Accepted", "Rejected"]:
        raise APIError("Status must be Accepted or Rejected", 400)

    db = get_db()
    sub_request = db.get(SubstituteRequest, request_id)
    if not sub_request:
        raise APIError("Substitute request not found", 404)

    if sub_request.recommended_id != user.id:
        raise APIError("Only the recommended faculty can respond", 403)

    if sub_request.status != "Pending":
        raise APIError("Request has already been processed", 400)

    sub_request.status = status_val
    db.commit()
    db.refresh(sub_request)

    return jsonify({
        "message": f"Substitute request {status_val.lower()}",
        "request_id": sub_request.id,
        "status": sub_request.status,
        "faculty": user.name
    }), 200
