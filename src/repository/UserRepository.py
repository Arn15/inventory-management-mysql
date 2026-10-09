def authenticate_user(conn, user_id):
    cursor = conn.cursor()
    query = "SELECT role_code FROM user WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()

    return row[0] if row else None
