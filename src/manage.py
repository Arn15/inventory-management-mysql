"""Administration commands (run with the admin database account from .env).

  python src/manage.py init-db                 create schema, procedures, triggers, seed data,
                                               least-privilege accounts and user passwords
  python src/manage.py create-db-accounts      (re)create the application database accounts
  python src/manage.py set-password USER_ID    set or reset an application user's password
  python src/manage.py unlock USER_ID          clear a lockout
  python src/manage.py audit [--limit N]       show recent audit events
"""
import argparse
import getpass
import os
import sys

from security import passwords, privileges
from utils import DBUtils, init, settings


def _quote_account(user: str, host: str) -> str:
    return f"'{user}'@'{host}'"


def create_db_accounts(conn) -> None:
    db = settings.db_settings()["database"]
    host = settings.account_host()
    cur = conn.cursor()
    for role, (user, _env) in settings.ACCOUNTS.items():
        _, password = settings.account_credentials(role)
        acct = _quote_account(user, host)
        cur.execute(f"DROP USER IF EXISTS {acct}")
        cur.execute(f"CREATE USER {acct} IDENTIFIED BY %s", (password,))
        for stmt in privileges.grant_statements(db, acct, role):
            cur.execute(stmt)
        print(f"  account {acct}: {role.lower()} privileges")
    cur.execute("FLUSH PRIVILEGES")
    conn.commit()
    cur.close()


def set_user_passwords(conn, demo_password: str | None) -> None:
    """Give every seeded application user a password (random unless one is supplied)."""
    cur = conn.cursor()
    cur.execute("SELECT user_id, role_code FROM User ORDER BY user_id")
    users = cur.fetchall()
    rows = []
    for user_id, role in users:
        pw = demo_password or passwords.generate_password()
        cur.execute("UPDATE User SET password_hash = %s, failed_attempts = 0, locked_until = NULL "
                    "WHERE user_id = %s", (passwords.hash_password(pw), user_id))
        rows.append((user_id, role, pw))
    conn.commit()
    cur.close()
    if demo_password:
        print(f"  all {len(rows)} users use the DEMO_USER_PASSWORD from .env")
    else:
        print("  initial passwords (shown once; change with set-password):")
        for user_id, role, pw in rows:
            print(f"    {user_id:<8} {role:<13} {pw}")


def cmd_init_db(args) -> None:
    db = settings.db_settings()["database"]
    conn = DBUtils.connect_admin(database=None)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db}`")
    cur.execute(f"USE `{db}`")
    cur.close()
    print(f"Initialising database {db} (this drops and recreates all tables)")
    init.create_schema(conn)
    create_db_accounts(conn)
    set_user_passwords(conn, os.environ.get("DEMO_USER_PASSWORD") or None)
    conn.close()
    print("Done. Start the app with: python src/app.py")


def cmd_create_accounts(args) -> None:
    conn = DBUtils.connect_admin()
    create_db_accounts(conn)
    conn.close()


def cmd_set_password(args) -> None:
    pw = getpass.getpass(f"New password for {args.user_id}: ")
    if pw != getpass.getpass("Repeat: "):
        sys.exit("Passwords do not match")
    try:
        hashed = passwords.hash_password(pw)
    except ValueError as e:
        sys.exit(str(e))
    conn = DBUtils.connect_admin()
    cur = conn.cursor()
    cur.execute("UPDATE User SET password_hash = %s, failed_attempts = 0, locked_until = NULL "
                "WHERE user_id = %s", (hashed, args.user_id))
    if cur.rowcount == 0:
        sys.exit(f"No such user: {args.user_id}")
    cur.execute("INSERT INTO Audit_Log (app_user, db_account, action, table_name, details) "
                "VALUES (%s, USER(), 'PASSWORD_SET', 'User', 'by admin')", (args.user_id,))
    conn.commit()
    conn.close()
    print("Password updated.")


def cmd_unlock(args) -> None:
    conn = DBUtils.connect_admin()
    cur = conn.cursor()
    cur.execute("UPDATE User SET failed_attempts = 0, locked_until = NULL WHERE user_id = %s", (args.user_id,))
    cur.execute("INSERT INTO Audit_Log (app_user, db_account, action, table_name, details) "
                "VALUES (%s, USER(), 'UNLOCK', 'User', 'by admin')", (args.user_id,))
    conn.commit()
    conn.close()
    print(f"{args.user_id} unlocked.")


def cmd_audit(args) -> None:
    conn = DBUtils.connect_admin()
    cur = conn.cursor()
    cur.execute("SELECT event_time, app_user, db_account, action, table_name, record_key, details "
                "FROM Audit_Log ORDER BY audit_id DESC LIMIT %s", (args.limit,))
    from tabulate import tabulate
    print(tabulate(cur.fetchall(), headers=["time", "app user", "db account", "action", "table", "key", "details"]))
    conn.close()


def main(argv=None):
    settings.load_env()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db").set_defaults(fn=cmd_init_db)
    sub.add_parser("create-db-accounts").set_defaults(fn=cmd_create_accounts)
    p = sub.add_parser("set-password"); p.add_argument("user_id"); p.set_defaults(fn=cmd_set_password)
    p = sub.add_parser("unlock"); p.add_argument("user_id"); p.set_defaults(fn=cmd_unlock)
    p = sub.add_parser("audit"); p.add_argument("--limit", type=int, default=30); p.set_defaults(fn=cmd_audit)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
