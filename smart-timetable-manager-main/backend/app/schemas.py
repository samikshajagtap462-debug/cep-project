from pydantic import BaseModel


# ==========================================================
# LOGIN
# ==========================================================

class LoginRequest(BaseModel):
    email: str
    password: str


class FacultyLoginRequest(BaseModel):
    email: str
    faculty_id: str
    password: str


class AdminLoginRequest(BaseModel):
    admin_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict = {}


# ==========================================================
# FACULTY
# ==========================================================

class FacultyCreate(BaseModel):
    name: str
    email: str
    password: str
    faculty_id: str | None = None
    role: str = "faculty"
    department: str = "AI&DS"
    expertise: list[str] = []
    max_hours: int = 16


class FacultyOut(BaseModel):
    id: int
    faculty_id: str | None = None
    name: str
    email: str
    role: str
    department: str = "AI&DS"
    expertise: list[str] = []
    max_hours: int = 16
    current_hours: int = 0


# ==========================================================
# TIMETABLE
# ==========================================================

class TimetableCreate(BaseModel):

    day: str

    start_time: str

    end_time: str

    subject: str

    class_name: str

    room: str

    faculty_id: int

    batch: str | None = None

    is_lab: bool = False


class TimetableOut(BaseModel):

    id: int

    day: str

    start_time: str

    end_time: str

    subject: str

    class_name: str

    room: str

    faculty_id: int

    faculty_name: str

    batch: str | None

    is_lab: bool