from flask import Blueprint, request, jsonify

from ..database import get_db
from ..models import Faculty, TimetableEntry, Subject, SyllabusTopic
from ..auth import current_user, APIError
from ..services.workload_service import (
    get_faculty_workload_detail,
    get_all_faculty_workloads,
    get_department_kpi_summary
)

router = Blueprint("analytics", __name__, url_prefix="/analytics")


# ==========================================================
# 1. FACULTY WORKLOAD ANALYTICS (CENTRALIZED SERVICE)
# ==========================================================

@router.route("/workload", methods=["GET"])
@current_user
def workload_analytics(user: Faculty):
    faculty_id = request.args.get("faculty_id", type=int)
    db = get_db()

    # Faculty data privacy: faculty members can only view their own workload
    if user.role == "faculty":
        if faculty_id is not None and faculty_id != user.id:
            raise APIError("Access denied: You can only view your own workload.", 403)
        faculty_list = [user]
    else:
        # Admin / HOD retains authorized access to department / specific faculty workload
        if faculty_id is not None:
            faculty_list = db.query(Faculty).filter(
                Faculty.id == faculty_id,
                Faculty.active == True
            ).all()
        else:
            # Department-wide workload: query active teaching faculty
            faculty_list = db.query(Faculty).filter(
                Faculty.department == user.department,
                Faculty.active == True
            ).order_by(Faculty.name).all()

    analytics = []
    for faculty in faculty_list:
        detail = get_faculty_workload_detail(db, faculty.id)
        # For general admin list, exclude pure administrative accounts with 0 sessions
        if user.role == "admin" and faculty_id is None and detail["is_administrative"] and not detail["has_verified_teaching"]:
            continue

        analytics.append({
            "faculty_id": faculty.id,
            "faculty_name": faculty.name,
            "faculty_code": detail["faculty_code"],
            "current_hours": detail["total_hours"],
            "total_sessions": detail["total_sessions"],
            "theory_sessions": detail["theory_sessions"],
            "practical_sessions": detail["practical_sessions"],
            "theory_hours": detail["theory_hours"],
            "practical_hours": detail["practical_hours"],
            "formatted_hours": detail["formatted_hours"],
            "max_hours": detail["max_hours"],
            "remaining_hours": detail["remaining_hours"],
            "workload_status": detail["workload_status"]
        })

    return jsonify({
        "department": user.department,
        "faculty_workload": analytics
    }), 200


# ==========================================================
# 2. SYLLABUS PROGRESS & VERIFIED TOPICS
# ==========================================================

@router.route("/syllabus", methods=["GET"])
@current_user
def syllabus_progress(user: Faculty):
    faculty_id = request.args.get("faculty_id", type=int)
    db = get_db()

    # Faculty data privacy: faculty members can only view their own syllabus progress
    if user.role == "faculty":
        if faculty_id is not None and faculty_id != user.id:
            raise APIError(
                "Access denied: You can only view your own syllabus progress.",
                403
            )
        target_faculty = user
    else:
        # Admin / HOD can view any faculty's syllabus progress
        if faculty_id is not None:
            target_faculty = db.get(Faculty, faculty_id)
            if not target_faculty:
                raise APIError("Faculty not found", 404)
        else:
            target_faculty = user

    subjects = db.query(Subject).filter(
        Subject.faculty_id == target_faculty.id
    ).all()

    progress = []
    for subject in subjects:
        # Check if topic-level records exist in database
        topics = db.query(SyllabusTopic).filter(SyllabusTopic.subject_id == subject.id).all()
        if topics:
            total_topics = len(topics)
            completed_topics = sum(1 for t in topics if t.status == "Completed")
            percentage = (completed_topics / total_topics) * 100 if total_topics > 0 else 0
            progress.append({
                "subject_id": subject.id,
                "subject": subject.name,
                "class_name": subject.class_name,
                "total_units": subject.total_units,
                "completed_units": subject.completed_units,
                "total_topics": total_topics,
                "completed_topics": completed_topics,
                "remaining_units": max(subject.total_units - subject.completed_units, 0),
                "progress_percentage": round(percentage, 2),
                "has_topics": True
            })
        else:
            total_units = subject.total_units
            completed_units = subject.completed_units
            percentage = (completed_units / total_units * 100) if total_units > 0 else 0
            progress.append({
                "subject_id": subject.id,
                "subject": subject.name,
                "class_name": subject.class_name,
                "total_units": total_units,
                "completed_units": completed_units,
                "total_topics": 0,
                "completed_topics": 0,
                "remaining_units": max(total_units - completed_units, 0),
                "progress_percentage": round(percentage, 2),
                "has_topics": False
            })

    return jsonify({
        "faculty": target_faculty.name,
        "department": target_faculty.department,
        "subjects": progress
    }), 200


@router.route("/syllabus/topics", methods=["GET"])
@current_user
def get_syllabus_topics(user: Faculty):
    subject_id = request.args.get("subject_id", type=int)
    if not subject_id:
        raise APIError("subject_id query parameter is required", 400)

    db = get_db()
    subject = db.get(Subject, subject_id)
    if not subject:
        raise APIError("Subject not found", 404)

    topics = db.query(SyllabusTopic).filter(
        SyllabusTopic.subject_id == subject_id
    ).order_by(SyllabusTopic.unit_number, SyllabusTopic.id).all()

    return jsonify({
        "subject_id": subject.id,
        "subject_name": subject.name,
        "class_name": subject.class_name,
        "topics": [
            {
                "id": t.id,
                "unit_number": t.unit_number,
                "unit_title": t.unit_title,
                "topic_name": t.topic_name,
                "planned_lectures": t.planned_lectures,
                "completed_lectures": t.completed_lectures,
                "target_date": t.target_date,
                "status": t.status
            }
            for t in topics
        ]
    }), 200


@router.route("/syllabus/topics", methods=["POST"])
@current_user
def create_syllabus_topic(user: Faculty):
    data = request.get_json(silent=True) or {}
    subject_id = data.get("subject_id")
    unit_title = data.get("unit_title", "").strip()
    topic_name = data.get("topic_name", "").strip()

    if not subject_id or not unit_title or not topic_name:
        raise APIError("subject_id, unit_title, and topic_name are required", 400)

    db = get_db()
    subject = db.get(Subject, subject_id)
    if not subject:
        raise APIError("Subject not found", 404)

    # Permission check: admin or assigned faculty
    if user.role != "admin" and subject.faculty_id != user.id:
        raise APIError("Access denied: You are not authorized to edit this syllabus.", 403)

    topic = SyllabusTopic(
        subject_id=subject_id,
        unit_number=int(data.get("unit_number", 1)),
        unit_title=unit_title,
        topic_name=topic_name,
        planned_lectures=int(data.get("planned_lectures", 2)),
        completed_lectures=int(data.get("completed_lectures", 0)),
        target_date=data.get("target_date"),
        status=data.get("status", "Pending")
    )
    db.add(topic)
    db.commit()

    return jsonify({
        "success": True,
        "topic": {
            "id": topic.id,
            "subject_id": topic.subject_id,
            "unit_number": topic.unit_number,
            "unit_title": topic.unit_title,
            "topic_name": topic.topic_name,
            "planned_lectures": topic.planned_lectures,
            "completed_lectures": topic.completed_lectures,
            "target_date": topic.target_date,
            "status": topic.status
        }
    }), 201


@router.route("/syllabus/topics/<int:topic_id>", methods=["PUT"])
@current_user
def update_syllabus_topic(user: Faculty, topic_id: int):
    db = get_db()
    topic = db.get(SyllabusTopic, topic_id)
    if not topic:
        raise APIError("Topic not found", 404)

    subject = db.get(Subject, topic.subject_id)
    if user.role != "admin" and (not subject or subject.faculty_id != user.id):
        raise APIError("Access denied: You are not authorized to update this topic.", 403)

    data = request.get_json(silent=True) or {}
    if "status" in data:
        topic.status = str(data["status"]).capitalize()
    if "completed_lectures" in data:
        topic.completed_lectures = int(data["completed_lectures"])
    if "planned_lectures" in data:
        topic.planned_lectures = int(data["planned_lectures"])
    if "target_date" in data:
        topic.target_date = data["target_date"]

    db.commit()

    return jsonify({
        "success": True,
        "topic": {
            "id": topic.id,
            "subject_id": topic.subject_id,
            "unit_number": topic.unit_number,
            "unit_title": topic.unit_title,
            "topic_name": topic.topic_name,
            "planned_lectures": topic.planned_lectures,
            "completed_lectures": topic.completed_lectures,
            "target_date": topic.target_date,
            "status": topic.status
        }
    }), 200


# ==========================================================
# 3. DASHBOARD STATISTICS
# ==========================================================

@router.route("/dashboard", methods=["GET"])
@current_user
def dashboard_statistics(user: Faculty):
    db = get_db()

    if user.role == "faculty":
        # Faculty member sees strictly their own timetable assignments and syllabus stats
        timetable_count = db.query(TimetableEntry).filter(
            TimetableEntry.faculty_id == user.id
        ).count()

        subject_count = db.query(Subject).filter(
            Subject.faculty_id == user.id
        ).count()

        total_units = 0
        completed_units = 0
        subjects = db.query(Subject).filter(
            Subject.faculty_id == user.id
        ).all()

        for subject in subjects:
            total_units += subject.total_units
            completed_units += subject.completed_units

        syllabus_percentage = (
            (completed_units / total_units * 100) if total_units > 0 else 0
        )
        remaining_units = max(total_units - completed_units, 0)

        fac_workload = get_faculty_workload_detail(db, user.id)

        return jsonify({
            "faculty": user.name,
            "department": user.department,
            "assigned_classes": timetable_count,
            "subjects": subject_count,
            "total_syllabus_units": total_units,
            "completed_syllabus_units": completed_units,
            "remaining_syllabus_units": remaining_units,
            "syllabus_progress_percentage": round(syllabus_percentage, 2),
            "weekly_teaching_hours": fac_workload["total_hours"],
            "formatted_weekly_hours": fac_workload["formatted_hours"]
        }), 200
    else:
        # Admin / HOD sees institutional department stats
        kpis = get_department_kpi_summary(db)
        subject_count = db.query(Subject).count()

        total_units = 0
        completed_units = 0
        subjects = db.query(Subject).all()

        for subject in subjects:
            total_units += subject.total_units
            completed_units += subject.completed_units

        syllabus_percentage = (
            (completed_units / total_units * 100) if total_units > 0 else 0
        )
        remaining_units = max(total_units - completed_units, 0)

        return jsonify({
            "admin": user.name,
            "department": user.department,
            "faculty_count": kpis["teaching_faculty_count"],
            "assigned_classes": kpis["total_scheduled_sessions"],
            "subjects": subject_count,
            "total_syllabus_units": total_units,
            "completed_syllabus_units": completed_units,
            "remaining_syllabus_units": remaining_units,
            "syllabus_progress_percentage": round(syllabus_percentage, 2),
            "total_teaching_hours": kpis["total_teaching_hours"],
            "formatted_total_hours": kpis["formatted_total_hours"]
        }), 200
