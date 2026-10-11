"""Password hashing with bcrypt."""
from __future__ import annotations

import secrets
import string

import bcrypt

BCRYPT_ROUNDS = 12
MIN_LENGTH = 12
MAX_BYTES = 72          # bcrypt ignores anything past 72 bytes, so reject longer passwords

# Hash of a random value, used to spend the same time on unknown user IDs as on real ones
# (prevents telling valid user IDs apart by response time).
DUMMY_HASH = bcrypt.hashpw(secrets.token_bytes(16), bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def validate_new_password(password: str) -> None:
    if len(password) < MIN_LENGTH:
        raise ValueError(f"Password must be at least {MIN_LENGTH} characters")
    if len(password.encode()) > MAX_BYTES:
        raise ValueError(f"Password must be at most {MAX_BYTES} bytes")


def hash_password(password: str) -> str:
    validate_new_password(password)
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(BCRYPT_ROUNDS)).decode()


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash or len(password.encode()) > MAX_BYTES:
        bcrypt.checkpw(b"x", DUMMY_HASH.encode())     # equalise timing
        return False
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:                                  # malformed stored hash
        return False


def generate_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits + "-_.!@#"
    return "".join(secrets.choice(alphabet) for _ in range(length))
