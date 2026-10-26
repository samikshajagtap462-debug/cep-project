from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Faculty, TimetableEntry
from ..security import hash_password
from ..auth import current_user, require_admin, APIError

router = Blueprint("faculty", __name__, url_prefix="/faculty")


def calculate_hours(db: Session, faculty_id: int) -> int:
    return db.query(TimetableEntry).filter(
        TimetableEntry.faculty_id == faculty_id
    ).count()


def faculty_response(faculty: Faculty, db: Session) -> dict:
    assigned_code = faculty.faculty_id or (f"FAC-{100 + faculty.id}" if faculty.role == "faculty" else "ADM-101")
    return {
        "id": faculty.id,
        "faculty_id": assigned_code,
        "name": faculty.name,
        "email": faculty.email,
        "role": faculty.role,
        "department": getattr(faculty, "department", "AI&DS"),
        "expertise": [
            x.strip()
            for x in faculty.expertise.split(",")
            if x.strip()
        ] if faculty.expertise else [],
        "max_hours": faculty.max_hours,
        "current_hours": calculate_hours(db, faculty.id)
    }


# ==========================================================
# GET ALL FACULTY
# ==========================================================

@router.route("", methods=["GET"])
@current_user
def get_all_faculty(user: Faculty):
    db = get_db()
    # Faculty data privacy: faculty members can only view their own faculty details
    if user.role == "faculty":
        return jsonify([faculty_response(user, db)]), 200

    # Admin / HOD access remains unchanged
    faculty_list = db.query(Faculty).filter(Faculty.active == True).all()
    return jsonify([faculty_response(f, db) for f in faculty_list]), 200


# ==========================================================
# GET SINGLE FACULTY
# ==========================================================

@router.route("/<int:faculty_id>", methods=["GET"])
@current_user
def get_faculty(faculty_id: int, user: Faculty):
    if user.role == "faculty" and user.id != faculty_id:
        raise APIError(
            "Access denied: You are only authorized to view your own faculty details.",
            403
        )

    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    return jsonify(faculty_response(faculty, db)), 200


# ==========================================================
# CREATE FACULTY (ADMIN ONLY)
# ==========================================================

@router.route("", methods=["POST"])
@require_admin
def create_faculty(admin: Faculty):
    data = request.get_json(silent=True) or {}
    clean_email = str(data.get("email", "")).strip().lower()

    if not clean_email or not data.get("name") or not data.get("password"):
        raise APIError("Name, email, and password are required.", 400)

    db = get_db()
    existing = db.query(Faculty).filter(Faculty.email == clean_email).first()
    if existing:
        raise APIError("Faculty with this email already exists", 409)

    next_id = db.query(Faculty).count() + 1
    new_faculty_code = data.get("faculty_id") or f"FAC-{100 + next_id}"

    expertise_val = data.get("expertise", [])
    if isinstance(expertise_val, list):
        expertise_str = ",".join(str(x) for x in expertise_val)
    else:
        expertise_str = str(expertise_val or "")

    faculty = Faculty(
        name=str(data.get("name", "")).strip(),
        email=clean_email,
        faculty_id=new_faculty_code,
        password_hash=hash_password(str(data.get("password", ""))),
        role=data.get("role") or "faculty",
        department=data.get("department") or "AI&DS",
        expertise=expertise_str,
        max_hours=int(data.get("max_hours", 16)),
        active=True
    )

    db.add(faculty)
    db.commit()
    db.refresh(faculty)

    return jsonify(faculty_response(faculty, db)), 200


# ==========================================================
# UPDATE FACULTY (ADMIN ONLY)
# ==========================================================

@router.route("/<int:faculty_id>", methods=["PUT"])
@require_admin
def update_faculty(faculty_id: int, admin: Faculty):
    data = request.get_json(silent=True) or {}
    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    if "name" in data:
        faculty.name = str(data["name"]).strip()
    if "email" in data:
        faculty.email = str(data["email"]).strip().lower()
    if "role" in data:
        faculty.role = data["role"]
    if "department" in data:
        faculty.department = data["department"]
    if "max_hours" in data:
        faculty.max_hours = int(data["max_hours"])
    if "expertise" in data:
        exp = data["expertise"]
        faculty.expertise = ",".join(str(x) for x in exp) if isinstance(exp, list) else str(exp)
    if data.get("password"):
        faculty.password_hash = hash_password(str(data["password"]))

    db.commit()
    db.refresh(faculty)

    return jsonify(faculty_response(faculty, db)), 200


# ==========================================================
# DEACTIVATE FACULTY (ADMIN ONLY)
# ==========================================================

@router.route("/<int:faculty_id>", methods=["DELETE"])
@require_admin
def delete_faculty(faculty_id: int, admin: Faculty):
    db = get_db()
    faculty = db.get(Faculty, faculty_id)
    if not faculty:
        raise APIError("Faculty not found", 404)

    faculty.active = False
    db.commit()

    return jsonify({
        "message": "Faculty deactivated successfully",
        "faculty_id": faculty_id
    }), 200
