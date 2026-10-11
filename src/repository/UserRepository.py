"""Authentication data access (used with the narrow inv_auth account)."""


def get_auth_record(conn, user_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, role_code, password_hash, "
        "       (locked_until IS NOT NULL AND locked_until > NOW()) AS is_locked "
        "FROM User WHERE user_id = %s",
        (user_id,))
    row = cursor.fetchone()
    cursor.close()
    return row


def record_failed_attempt(conn, user_id, max_attempts, lock_minutes):
    """Increment the failure counter; on reaching max_attempts, lock and reset the counter.

    locked_until is assigned first so both expressions see the old failed_attempts value
    (MySQL evaluates single-table UPDATE assignments left to right).
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE User SET "
        "  locked_until = IF(failed_attempts + 1 >= %s, NOW() + INTERVAL %s MINUTE, locked_until), "
        "  failed_attempts = IF(failed_attempts + 1 >= %s, 0, failed_attempts + 1) "
        "WHERE user_id = %s",
        (max_attempts, lock_minutes, max_attempts, user_id))
    conn.commit()
    cursor.close()


def record_successful_login(conn, user_id):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE User SET failed_attempts = 0, locked_until = NULL, last_login = NOW() WHERE user_id = %s",
        (user_id,))
    conn.commit()
    cursor.close()
