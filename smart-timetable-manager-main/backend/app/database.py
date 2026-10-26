import os
import shutil
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Base backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLED_DB_PATH = os.path.join(BASE_DIR, "edunova.db")


def resolve_database_config():
    """
    Determines the database URL and active SQLite file path with Render persistent disk support.
    
    Priority order:
    1. Explicit DATABASE_PATH or SQLITE_DB_PATH environment variable (e.g. /var/data/edunova.db)
    2. Explicit DATABASE_URL environment variable (supports postgresql:// and sqlite:///)
    3. Auto-detected Render persistent disk: if /var/data directory exists -> /var/data/edunova.db
    4. Fallback to bundled project database: backend/edunova.db

    Safe One-Time Initialization:
    If using SQLite on a persistent disk (or any target path differing from bundled DB),
    and target file does not yet exist:
    - Safely copies the bundled template database containing existing data to target_path.
    - If target file already exists, it is NEVER overwritten.
    """
    db_path = None
    database_url = os.getenv("DATABASE_URL")
    explicit_path = os.getenv("DATABASE_PATH") or os.getenv("SQLITE_DB_PATH")

    if explicit_path:
        db_path = os.path.abspath(explicit_path)
    elif database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
            return database_url, None
        elif database_url.startswith("postgresql://"):
            return database_url, None
        elif database_url.startswith("sqlite:///"):
            raw_path = database_url[len("sqlite:///"):]
            db_path = os.path.abspath(raw_path)
    else:
        # Check for Render persistent disk mount at /var/data
        if os.path.isdir("/var/data") and os.access("/var/data", os.W_OK):
            db_path = "/var/data/edunova.db"
        else:
            db_path = BUNDLED_DB_PATH

    # For SQLite, perform safe one-time copy if persistent target does not exist
    if db_path:
        target_dir = os.path.dirname(os.path.abspath(db_path))
        if target_dir and not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
            except OSError as e:
                logger.warning(f"Could not create database directory {target_dir}: {e}")

        # If target file exists, preserve it completely
        if os.path.exists(db_path):
            logger.info(f"Using existing SQLite database at '{db_path}' ({os.path.getsize(db_path)} bytes).")
        else:
            # Persistent disk is empty on first deployment; safely initialize once from secret file or bundled template
            secret_source = os.getenv("SECRET_DB_PATH") or "/etc/secrets/edunova.db"
            init_source = None
            if os.path.exists(secret_source):
                init_source = secret_source
            elif os.path.exists(BUNDLED_DB_PATH) and os.path.abspath(db_path) != os.path.abspath(BUNDLED_DB_PATH):
                init_source = BUNDLED_DB_PATH

            if init_source:
                try:
                    shutil.copy2(init_source, db_path)
                    logger.info(
                        f"Initialized persistent database at '{db_path}' "
                        f"from source '{init_source}' ({os.path.getsize(db_path)} bytes)."
                    )
                except Exception as e:
                    logger.error(f"Failed to copy database from '{init_source}' to '{db_path}': {e}. Falling back to bundled DB.")
                    db_path = BUNDLED_DB_PATH

        norm_path = os.path.abspath(db_path).replace("\\", "/")
        database_url = f"sqlite:///{norm_path}"

    return database_url, db_path


DATABASE_URL, DB_PATH = resolve_database_config()
if not DB_PATH:
    DB_PATH = BUNDLED_DB_PATH

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


def get_db():
    """
    Returns an active database session.
    When running within a Flask request context, attaches to flask.g so the session
    is scoped to the request and automatically closed on teardown.
    Otherwise, creates and returns a standalone SessionLocal.
    """
    try:
        from flask import g, has_app_context
        if has_app_context():
            if not hasattr(g, "db") or g.db is None:
                g.db = SessionLocal()
            return g.db
    except ImportError:
        pass

    return SessionLocal()
