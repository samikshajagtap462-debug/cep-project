from sqlalchemy.orm import Session

from ..models import Faculty, TimetableEntry


def recommend_substitutes(
    db: Session,
    day: str,
    start_time: str,
    end_time: str,
    subject: str
):
    # Get all active faculty
    faculty_list = (
        db.query(Faculty)
        .filter(Faculty.active == True)
        .all()
    )

    recommendations = []

    for faculty in faculty_list:

        # Check if faculty already has a lecture at this time
        busy = (
            db.query(TimetableEntry)
            .filter(
                TimetableEntry.faculty_id == faculty.id,
                TimetableEntry.day == day,
                TimetableEntry.start_time == start_time,
                TimetableEntry.end_time == end_time
            )
            .first()
        )

        # Skip busy faculty
        if busy:
            continue

        # Calculate current workload
        workload = (
            db.query(TimetableEntry)
            .filter(TimetableEntry.faculty_id == faculty.id)
            .count()
        )

        # Check subject expertise
        expertise_match = (
            subject.lower() in faculty.expertise.lower()
            if faculty.expertise
            else False
        )

        recommendations.append({
            "faculty_id": faculty.id,
            "name": faculty.name,
            "expertise_match": expertise_match,
            "current_workload": workload,
            "max_hours": faculty.max_hours
        })

    # Put subject-expertise matches first,
    # then lower workload
    recommendations.sort(
        key=lambda x: (
            not x["expertise_match"],
            x["current_workload"]
        )
    )

    return recommendations