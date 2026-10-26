from flask import Blueprint, request, jsonify

from ..database import get_db
from ..models import Room, TimetableEntry, Faculty
from ..auth import current_user, APIError
from ..formatters import format_display_class

router = Blueprint("rooms", __name__, url_prefix="/rooms")


# ==========================================================
# ROOM OCCUPANCY
# ==========================================================

@router.route("/occupancy", methods=["GET"])
@current_user
def room_occupancy(user: Faculty):
    day = request.args.get("day")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    if not day or not start_time or not end_time:
        raise APIError("day, start_time, and end_time parameters are required", 400)

    db = get_db()
    rooms = db.query(Room).filter(Room.active == True).all()

    occupied_rooms = []
    available_rooms = []

    for room in rooms:
        entries = db.query(TimetableEntry).filter(
            TimetableEntry.room == room.name,
            TimetableEntry.day == day
        ).all()

        overlapping = []
        for entry in entries:
            # True interval overlap: start1 < end2 AND start2 < end1
            if start_time < entry.end_time and entry.start_time < end_time:
                overlapping.append(entry)

        occupied = len(overlapping) > 0
        has_conflict = len(overlapping) > 1

        primary_session = None
        sessions_data = []
        for entry in overlapping:
            fac_name = entry.faculty.name if entry.faculty else "Unassigned"
            sess_obj = {
                "id": entry.id,
                "subject": entry.subject,
                "class_name": entry.class_name,
                "batch": entry.batch,
                "class_div": format_display_class(entry.class_name, entry.batch, entry.is_lab, getattr(entry, "session_type", "Practical" if entry.is_lab else "Theory")),
                "faculty_id": entry.faculty_id,
                "faculty_name": fac_name,
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "session_type": getattr(entry, "session_type", "Practical" if entry.is_lab else "Theory"),
                "is_lab": bool(entry.is_lab)
            }
            sessions_data.append(sess_obj)
            if not primary_session:
                primary_session = sess_obj

        room_info = {
            "room_id": room.id,
            "room_name": room.name,
            "room_type": room.room_type,
            "capacity": room.capacity,
            "is_lab": bool(getattr(room, "is_lab", False) or "lab" in (room.room_type or "").lower() or room.name.startswith("Lab") or room.name in ("AI1", "AI2", "CN1", "IIOT", "ARVR", "IOT", "Room 609A", "Room 609B")),
            "status": "Occupied" if occupied else "Available",
            "has_conflict": has_conflict,
            "session": primary_session,
            "sessions": sessions_data
        }

        if occupied:
            occupied_rooms.append(room_info)
        else:
            available_rooms.append(room_info)

    return jsonify({
        "day": day,
        "start_time": start_time,
        "end_time": end_time,
        "occupied_rooms": occupied_rooms,
        "available_rooms": available_rooms
    }), 200
