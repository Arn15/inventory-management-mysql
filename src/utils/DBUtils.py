"""Database connections and stored-procedure helper."""
from __future__ import annotations

import mysql.connector
from mysql.connector import Error

from utils import settings


def create_connection(user: str, password: str, database: str | None = "__default__"):
    """Open a connection with explicit credentials (no defaults to root)."""
    s = settings.db_settings()
    db = s["database"] if database == "__default__" else database
    kwargs = dict(host=s["host"], port=s["port"], user=user, password=password)
    if db:
        kwargs["database"] = db
    return mysql.connector.connect(**kwargs)


def connect_as(account_key: str, app_user: str | None = None):
    """Connect with the least-privilege account for a role ('AUTH', 'MANUFACTURER', ...).

    app_user is stored in the session variable @app_user, which the audit triggers record.
    """
    user, password = settings.account_credentials(account_key)
    conn = create_connection(user, password)
    if app_user is not None:
        cur = conn.cursor()
        cur.execute("SET @app_user = %s", (app_user,))
        cur.close()
    return conn


def connect_admin(database: str | None = "__default__"):
    user, password = settings.admin_credentials()
    return create_connection(user, password, database)


def execute_stored_procedure(conn, proc_name, params=None):
    """ Execute a stored procedure with given parameters """
    cursor = None
    try:
        cursor = conn.cursor()
        if params:
            cursor.callproc(proc_name, params)
        else:
            cursor.callproc(proc_name)
        conn.commit()
        results = []
        for result in cursor.stored_results():
            results.append(result.fetchall())
        return results
    except Error as e:
        print(f"Error executing stored procedure: {e}")
        conn.rollback()
        return None
    finally:
        if cursor is not None:
            cursor.close()

# Removed: get_data_from_table() built SQL with f-strings from its arguments (table name and
# WHERE clause), an SQL injection risk, and process_order() called procedures that do not
# exist. Neither was used anywhere.
