def log_event(conn, app_user, action, details=None):
    """Append an authentication event to Audit_Log (data changes are logged by triggers)."""
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Audit_Log (app_user, db_account, action, table_name, details) "
        "VALUES (%s, USER(), %s, 'User', %s)",
        (app_user[:10] if app_user else None, action, details))
    conn.commit()
    cursor.close()
