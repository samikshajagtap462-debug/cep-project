"""Shared Centralized Workload Calculation Service.

Calculates authentic teaching workload durations from actual scheduled sessions
stored in SQLite. Duration is calculated from the exact start and end time interval.
Excludes pure administrative accounts (e.g. ADM-101 with 0 teaching duties)
from teaching faculty statistics, while honoring verified teaching assignments
for designated HOD accounts (e.g. Dr. Dhanraj R. Dhotre).
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models import Faculty, TimetableEntry, SubstituteRequest


def calculate_session_duration(start_time: str, end_time: str) -> float:
    """Calculate exact duration in hours from start_time and end_time (HH:MM)."""
    try:
        sh, sm = map(int, str(start_time).strip().split(":"))
        eh, em = map(int, str(end_time).strip().split(":"))
        diff_minutes = (eh * 60 + em) - (sh * 60 + sm)
        return max(0.0, round(diff_minutes / 60.0, 2))
    except (ValueError, TypeError, AttributeError):
        return 1.0


def format_hours_string(hours: float) -> str:
    """Format decimal hours to a clean string e.g. '16 hrs/wk' or '14.5 hrs/wk'."""
    if hours == int(hours):
        return f"{int(hours)} hrs/wk"
    return f"{hours:.1f} hrs/wk"


def get_faculty_workload_detail(db: Session, faculty_id: int) -> Dict[str, Any]:
    """Calculate comprehensive, accurate teaching workload for a specific faculty member."""
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        return {
            "faculty_id": faculty_id,
            "faculty_name": "Unknown",
            "role": "unknown",
            "is_administrative": False,
            "has_verified_teaching": False,
            "total_sessions": 0,
            "theory_sessions": 0,
            "practical_sessions": 0,
            "total_hours": 0.0,
            "theory_hours": 0.0,
            "practical_hours": 0.0,
            "formatted_hours": "0 hrs/wk",
            "max_hours": 16,
            "remaining_hours": 16.0,
            "workload_status": "Low",
            "days_breakdown": {}
        }

    # Fetch all timetable entries for this faculty
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.faculty_id == faculty.id
    ).order_by(TimetableEntry.day, TimetableEntry.start_time).all()

    theory_sessions = 0
    practical_sessions = 0
    theory_hours = 0.0
    practical_hours = 0.0

    days_breakdown: Dict[str, Dict[str, Any]] = {
        d: {"day": d, "theory_count": 0, "practical_count": 0, "total_sessions": 0, "hours": 0.0, "sessions": []}
        for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    }

    for entry in entries:
        is_lab = bool(entry.is_lab or getattr(entry, "session_type", "") == "Practical")
        dur = calculate_session_duration(entry.start_time, entry.end_time)

        if is_lab:
            practical_sessions += 1
            practical_hours += dur
        else:
            theory_sessions += 1
            theory_hours += dur

        day_name = str(entry.day).capitalize() if entry.day else "Monday"
        if day_name in days_breakdown:
            if is_lab:
                days_breakdown[day_name]["practical_count"] += 1
            else:
                days_breakdown[day_name]["theory_count"] += 1
            days_breakdown[day_name]["total_sessions"] += 1
            days_breakdown[day_name]["hours"] = round(days_breakdown[day_name]["hours"] + dur, 2)
            days_breakdown[day_name]["sessions"].append({
                "id": entry.id,
                "subject": entry.subject,
                "class_name": entry.class_name,
                "batch": entry.batch,
                "room": entry.room,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "duration": dur,
                "is_lab": is_lab
            })

    total_sessions = theory_sessions + practical_sessions
    total_hours = round(theory_hours + practical_hours, 2)
    max_hours = faculty.max_hours or 16
    remaining_hours = max(0.0, round(max_hours - total_hours, 2))

    # Workload status category
    if total_hours >= max_hours:
        workload_status = "Full"
    elif total_hours >= max_hours * 0.75:
        workload_status = "High"
    elif total_hours >= max_hours * 0.50:
        workload_status = "Medium"
    else:
        workload_status = "Low"

    is_admin = faculty.role == "admin"
    has_teaching = total_sessions > 0

    return {
        "faculty_id": faculty.id,
        "faculty_code": faculty.faculty_id or (f"FAC-{100 + faculty.id}" if not is_admin else "ADM-101"),
        "faculty_name": faculty.name,
        "email": faculty.email,
        "role": faculty.role,
        "department": faculty.department or "AI&DS",
        "designation": "HOD / Administrator" if is_admin else ("Professor" if "Dr." in faculty.name else "Assistant Professor"),
        "is_administrative": is_admin,
        "has_verified_teaching": has_teaching,
        "total_sessions": total_sessions,
        "theory_sessions": theory_sessions,
        "practical_sessions": practical_sessions,
        "total_hours": total_hours,
        "theory_hours": round(theory_hours, 2),
        "practical_hours": round(practical_hours, 2),
        "formatted_hours": format_hours_string(total_hours),
        "max_hours": max_hours,
        "remaining_hours": remaining_hours,
        "workload_status": workload_status,
        "days_breakdown": days_breakdown
    }


def get_all_faculty_workloads(db: Session, include_admin_without_teaching: bool = False) -> List[Dict[str, Any]]:
    """Retrieve consistent workload metrics for all eligible faculty members.
    
    Excludes pure administrative accounts (e.g. ADM-101 with 0 sessions) by default.
    """
    faculties = db.query(Faculty).filter(Faculty.active == True).order_by(Faculty.name).all()
    results = []

    for f in faculties:
        detail = get_faculty_workload_detail(db, f.id)
        # Exclude administrative accounts that have no teaching duties
        if detail["is_administrative"] and not detail["has_verified_teaching"] and not include_admin_without_teaching:
            continue
        results.append(detail)

    return results


def get_department_kpi_summary(db: Session) -> Dict[str, Any]:
    """Calculate institutional department workload KPIs from authoritative SQLite database."""
    workloads = get_all_faculty_workloads(db, include_admin_without_teaching=False)

    total_sessions = sum(w["total_sessions"] for w in workloads)
    total_theory = sum(w["theory_sessions"] for w in workloads)
    total_practical = sum(w["practical_sessions"] for w in workloads)
    total_hours = round(sum(w["total_hours"] for w in workloads), 2)
    teaching_faculty_count = len(workloads)

    return {
        "total_scheduled_sessions": total_sessions,
        "theory_sessions": total_theory,
        "practical_sessions": total_practical,
        "total_teaching_hours": total_hours,
        "teaching_faculty_count": teaching_faculty_count,
        "formatted_total_hours": format_hours_string(total_hours)
    }
