"""Password authentication with account lockout.

* bcrypt-hashed passwords; users without a password set cannot log in
* 5 consecutive failures lock the account for 15 minutes
* unknown user IDs, wrong passwords and locked accounts all return the same result and
  take about the same time, so the login screen does not reveal which user IDs exist
* every attempt is written to Audit_Log
"""
from repository import AuditRepository, UserRepository
from security.passwords import verify_password

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
VALID_ROLES = {"MANUFACTURER", "SUPPLIER", "VIEWER"}


def authenticate(conn, user_id, password):
    """Return the user's role on success, otherwise None."""
    user_id = (user_id or "").strip()
    record = UserRepository.get_auth_record(conn, user_id) if user_id else None

    if record is None:
        verify_password(password, None)                       # constant-time path
        AuditRepository.log_event(conn, user_id or None, "LOGIN_FAILED", "unknown user id")
        return None

    if record["is_locked"]:
        verify_password(password, None)
        AuditRepository.log_event(conn, user_id, "LOGIN_LOCKED", "attempt while account locked")
        return None

    if not verify_password(password, record["password_hash"]):
        UserRepository.record_failed_attempt(conn, user_id, MAX_FAILED_ATTEMPTS, LOCKOUT_MINUTES)
        AuditRepository.log_event(conn, user_id, "LOGIN_FAILED", "bad password")
        return None

    if record["role_code"] not in VALID_ROLES:                # fail closed
        AuditRepository.log_event(conn, user_id, "LOGIN_FAILED", "invalid role")
        return None

    UserRepository.record_successful_login(conn, user_id)
    AuditRepository.log_event(conn, user_id, "LOGIN_SUCCESS", record["role_code"])
    return record["role_code"]
