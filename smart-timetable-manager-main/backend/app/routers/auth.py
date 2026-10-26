import time
from collections import defaultdict
from flask import Blueprint, request, jsonify

from ..database import get_db
from ..models import Faculty
from ..security import verify_password, create_access_token
from ..auth import current_user, APIError

router = Blueprint("auth", __name__, url_prefix="/auth")

# ==========================================================
# RATE LIMITING (LOGIN ATTEMPT LIMITS)
# Maximum 5 failed attempts in 15 minutes per key/IP
# ==========================================================

FAILED_ATTEMPTS = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes


def get_client_ip() -> str:
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def check_rate_limit(key: str):
    now = time.time()
    valid_attempts = [t for t in FAILED_ATTEMPTS[key] if now - t < LOCKOUT_SECONDS]
    FAILED_ATTEMPTS[key] = valid_attempts

    if len(valid_attempts) >= MAX_ATTEMPTS:
        time_left = int(LOCKOUT_SECONDS - (now - valid_attempts[0]))
        minutes = max(1, (time_left + 59) // 60)
        raise APIError(
            f"Too many failed login attempts. Please try again after {minutes} minute(s).",
            429
        )


def record_failed_attempt(key: str):
    FAILED_ATTEMPTS[key].append(time.time())


def clear_failed_attempts(key: str):
    if key in FAILED_ATTEMPTS:
        del FAILED_ATTEMPTS[key]


# ==========================================================
# 1. FACULTY LOGIN
# Requires: Faculty Email ID, Faculty ID, and Password
# All 3 must match the same registered faculty account
# ==========================================================

@router.route("/login/faculty", methods=["POST"])
def login_faculty():
    data = request.get_json(silent=True) or {}
    ip = get_client_ip()
    email_clean = str(data.get("email", "")).strip().lower()
    fac_id_clean = str(data.get("faculty_id", "")).strip().upper()
    password = str(data.get("password", ""))
    rate_key = f"faculty:{email_clean}:{ip}"

    # Check attempt limits
    check_rate_limit(rate_key)

    # Validate non-empty fields
    if not email_clean or not fac_id_clean or not password:
        raise APIError(
            "Faculty Email ID, Faculty ID, and Password are all required.",
            400
        )

    # Normalize email domain to match DB (.edu or .local)
    alt_email = email_clean.replace("@edunova.edu", "@edunova.local") if "@edunova.edu" in email_clean else email_clean.replace("@edunova.local", "@edunova.edu")

    db = get_db()
    # Find faculty record
    user = db.query(Faculty).filter(
        (Faculty.email == email_clean) | (Faculty.email == alt_email)
    ).first()

    if not user:
        record_failed_attempt(rate_key)
        raise APIError("Invalid email, Faculty ID, or password.", 401)

    # Ensure role is faculty (strictly block admin from faculty endpoint)
    if user.role != "faculty":
        record_failed_attempt(rate_key)
        raise APIError("Invalid email, Faculty ID, or password.", 401)

    # Verify Faculty ID matches this account
    assigned_code = (user.faculty_id or f"FAC-{100 + user.id}").upper()
    valid_id_matches = {
        assigned_code,
        str(user.id),
        f"FAC-{user.id}"
    }

    if fac_id_clean not in valid_id_matches:
        record_failed_attempt(rate_key)
        raise APIError("Faculty ID does not match the registered account.", 401)

    # Verify password hash
    if not verify_password(password, user.password_hash):
        record_failed_attempt(rate_key)
        raise APIError("Invalid email, Faculty ID, or password.", 401)

    if not user.active:
        raise APIError(
            "User account is inactive. Please contact the administrator.",
            403
        )

    # Clear rate limit on successful authentication
    clear_failed_attempts(rate_key)

    token = create_access_token(user.id, user.role)

    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "faculty_id": assigned_code,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": user.department
        }
    }), 200


# ==========================================================
# 2. ADMIN / HOD LOGIN
# Requires: Admin ID / Email and Password
# Allows only authorized Admin/HOD accounts
# ==========================================================

@router.route("/login/admin", methods=["POST"])
def login_admin():
    data = request.get_json(silent=True) or {}
    ip = get_client_ip()
    admin_id_clean = str(data.get("admin_id", "")).strip()
    password = str(data.get("password", ""))
    rate_key = f"admin:{admin_id_clean.lower()}:{ip}"

    # Check attempt limits
    check_rate_limit(rate_key)

    if not admin_id_clean or not password:
        raise APIError("Admin ID / Email and Password are required.", 400)

    identifier_lower = admin_id_clean.lower()
    alt_email = identifier_lower.replace("@edunova.edu", "@edunova.local") if "@edunova.edu" in identifier_lower else identifier_lower.replace("@edunova.local", "@edunova.edu")

    db = get_db()
    # Find matching account by email or faculty_id
    user = db.query(Faculty).filter(
        (Faculty.email == identifier_lower) |
        (Faculty.email == alt_email) |
        (Faculty.faculty_id == admin_id_clean.upper())
    ).first()

    # Fallback if admin entered 'ADM-101' or 'admin' and not matched directly
    if not user and (identifier_lower == "admin" or admin_id_clean.upper() == "ADM-101"):
        user = db.query(Faculty).filter(Faculty.role == "admin").first()

    if not user:
        record_failed_attempt(rate_key)
        raise APIError("Invalid Admin ID or password.", 401)

    # Strictly disallow faculty accounts from accessing Admin dashboard
    if user.role != "admin":
        record_failed_attempt(rate_key)
        raise APIError(
            "Access denied. Faculty accounts cannot access the Admin/HOD portal.",
            403
        )

    # Verify password hash
    if not verify_password(password, user.password_hash):
        record_failed_attempt(rate_key)
        raise APIError("Invalid Admin ID or password.", 401)

    if not user.active:
        raise APIError("Admin account is inactive.", 403)

    clear_failed_attempts(rate_key)

    token = create_access_token(user.id, user.role)

    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "faculty_id": user.faculty_id or "ADM-101",
            "name": user.name,
            "email": user.email,
            "role": "admin",
            "department": user.department
        }
    }), 200


# ==========================================================
# 3. GENERIC LOGIN (Backward Compatible)
# ==========================================================

@router.route("/login", methods=["POST"])
def login_generic():
    data = request.get_json(silent=True) or {}
    ip = get_client_ip()
    email_clean = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    rate_key = f"generic:{email_clean}:{ip}"
    check_rate_limit(rate_key)

    alt_email = email_clean.replace("@edunova.edu", "@edunova.local") if "@edunova.edu" in email_clean else email_clean.replace("@edunova.local", "@edunova.edu")

    db = get_db()
    user = db.query(Faculty).filter(
        (Faculty.email == email_clean) | (Faculty.email == alt_email) | (Faculty.faculty_id == str(data.get("email", "")).strip().upper())
    ).first()

    if not user or not verify_password(password, user.password_hash):
        record_failed_attempt(rate_key)
        raise APIError("Invalid credentials.", 401)

    if not user.active:
        raise APIError("Account is inactive.", 403)

    clear_failed_attempts(rate_key)
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


# ==========================================================
# 4. CURRENT AUTHENTICATED USER
# ==========================================================

@router.route("/me", methods=["GET"])
@current_user
def get_me(user: Faculty):
    return jsonify({
        "id": user.id,
        "faculty_id": user.faculty_id or (f"FAC-{100 + user.id}" if user.role == "faculty" else "ADM-101"),
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "department": user.department,
        "expertise": [
            x.strip()
            for x in user.expertise.split(",")
            if x.strip()
        ] if user.expertise else []
    }), 200
