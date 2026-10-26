import hashlib
import hmac
import os

from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()


def get_secret_key() -> str:
    return (
        os.getenv("EDUNOVA_SECRET_KEY")
        or os.getenv("SECRET_KEY")
        or "edunova-secure-jwt-secret-key-2026"
    )


SECRET_KEY = get_secret_key()

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==========================================================
# PASSWORD HASHING
# ==========================================================

def hash_password(password: str):

    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120000
    )

    return salt.hex() + ":" + digest.hex()


# ==========================================================
# PASSWORD VERIFICATION
# ==========================================================

def verify_password(
    password: str,
    stored_password: str
):

    try:

        salt_hex, digest_hex = stored_password.split(":")

        salt = bytes.fromhex(salt_hex)

        expected = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            120000
        )

        return hmac.compare_digest(
            expected.hex(),
            digest_hex
        )

    except Exception:

        return False


# ==========================================================
# CREATE TOKEN
# ==========================================================

def create_access_token(
    user_id: int,
    role: str
):

    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expiration
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM
    )


# ==========================================================
# DECODE TOKEN
# ==========================================================

def decode_token(token: str):

    return jwt.decode(
        token,
        get_secret_key(),
        algorithms=[ALGORITHM]
    )