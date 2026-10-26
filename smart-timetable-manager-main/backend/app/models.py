from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .database import Base
from .formatters import format_display_class, extract_batch_letter

# ==========================================================
# CLASS MODEL TABLE
# ==========================================================

class ClassModel(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    academic_year: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True
    )  # 'SY', 'TY', 'BE'

    division: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )  # 'AD1', 'AD2', 'AD3'

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )  # 'SY-AD1', 'SY-AD2', etc.

    department: Mapped[str] = mapped_column(
        String(100),
        default="AI&DS"
    )

    batches = relationship(
        "Batch",
        back_populates="class_model",
        cascade="all, delete-orphan",
        lazy="joined"
    )


# ==========================================================
# BATCH MODEL TABLE
# ==========================================================

class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # 'Batch A', 'Batch B', 'Batch C'

    class_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=True
    )

    class_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    student_count: Mapped[int] = mapped_column(
        Integer,
        default=25
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    class_model = relationship("ClassModel", back_populates="batches")


# ==========================================================
# FACULTY TABLE
# ==========================================================

class Faculty(Base):

    __tablename__ = "faculty"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    faculty_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(300),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="faculty"
    )

    department: Mapped[str] = mapped_column(
        String(100),
        default="AI&DS"
    )

    expertise: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    max_hours: Mapped[int] = mapped_column(
        Integer,
        default=16
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    timetable = relationship(
        "TimetableEntry",
        back_populates="faculty",
        cascade="all, delete-orphan"
    )


# ==========================================================
# SUBJECT TABLE
# ==========================================================

class Subject(Base):

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False
    )

    code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    short_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    academic_year: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    total_units: Mapped[int] = mapped_column(
        Integer,
        default=6
    )

    completed_units: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    is_practical: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    faculty_id: Mapped[int | None] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=True
    )


# ==========================================================
# FACULTY ASSIGNMENTS TABLE
# ==========================================================

class FacultyAssignment(Base):
    __tablename__ = "faculty_assignments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=False
    )

    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=True
    )

    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.id"),
        nullable=False
    )

    batch: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )  # 'Batch A', 'Batch B', 'Batch C', or None (entire class)

    session_type: Mapped[str] = mapped_column(
        String(20),
        default="Theory"
    )  # 'Theory', 'Practical', 'Tutorial'

    faculty = relationship("Faculty")
    subject = relationship("Subject")
    class_model = relationship("ClassModel")


# ==========================================================
# TIMETABLE TABLE
# ==========================================================

class TimetableEntry(Base):

    __tablename__ = "timetable"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    day: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    start_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    end_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    subject: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    room: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    faculty_id: Mapped[int | None] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=True
    )

    batch: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    is_lab: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    session_type: Mapped[str] = mapped_column(
        String(30),
        default="Theory"
    )

    class_id: Mapped[int | None] = mapped_column(
        ForeignKey("classes.id"),
        nullable=True
    )

    subject_id: Mapped[int | None] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=True
    )

    academic_year: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    semester: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True
    )

    faculty = relationship(
        "Faculty",
        back_populates="timetable"
    )

    @property
    def display_class(self) -> str:
        return format_display_class(self.class_name, self.batch, self.is_lab, self.session_type)

    @property
    def batch_letter(self) -> str | None:
        return extract_batch_letter(self.batch)


# ==========================================================
# ROOM TABLE
# ==========================================================

class Room(Base):

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False
    )

    room_type: Mapped[str] = mapped_column(
        String(30),
        default="Classroom"
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        default=60
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )


# ==========================================================
# SUBSTITUTE REQUEST
# ==========================================================

class SubstituteRequest(Base):

    __tablename__ = "substitute_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id")
    )

    recommended_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id")
    )

    subject: Mapped[str] = mapped_column(
        String(120)
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        default=""
    )

    day: Mapped[str] = mapped_column(
        String(20),
        default=""
    )

    slot: Mapped[str] = mapped_column(
        String(50)
    )

    reason: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


# ==========================================================
# CONFLICT TABLE
# ==========================================================

class Conflict(Base):
    __tablename__ = "conflicts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=False
    )

    room: Mapped[str] = mapped_column(
        String(80),
        nullable=False
    )

    day: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    start_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    end_time: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    subject: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    class_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    conflict_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    resolved_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )

    faculty = relationship("Faculty", backref="conflicts")


# ==========================================================
# ADMIN NOTIFICATION TABLE
# ==========================================================

class AdminNotification(Base):
    __tablename__ = "admin_notifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    conflict_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conflicts.id"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    publisher_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=True
    )

    department: Mapped[Optional[str]] = mapped_column(
        String(100),
        default="AI&DS"
    )

    recipient_scope: Mapped[str] = mapped_column(
        String(50),
        default="all"
    )

    target_faculty_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=True
    )

    notification_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    conflict = relationship("Conflict", backref="notifications")
    publisher = relationship("Faculty", foreign_keys=[publisher_id])


class FacultyNotificationRead(Base):
    __tablename__ = "faculty_notification_reads"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("faculty.id"),
        nullable=False,
        index=True
    )

    notification_id: Mapped[int] = mapped_column(
        ForeignKey("admin_notifications.id"),
        nullable=False,
        index=True
    )

    read_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("faculty_id", "notification_id", name="uq_faculty_notification_read"),
    )


# ==========================================================
# SYLLABUS TOPIC TABLE
# ==========================================================

class SyllabusTopic(Base):
    __tablename__ = "syllabus_topics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id"),
        nullable=False
    )

    unit_number: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    unit_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    topic_name: Mapped[str] = mapped_column(
        String(250),
        nullable=False
    )

    planned_lectures: Mapped[int] = mapped_column(
        Integer,
        default=2
    )

    completed_lectures: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    target_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Pending"
    )

    subject = relationship("Subject", backref="topics")
