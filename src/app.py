"""Inventory Management CLI.

Run `python src/manage.py init-db` once to create the database; this program never
modifies the schema or reloads seed data.
"""
import getpass
import sys

from factory import ViewFactory
from service import LoginService
from utils import DBUtils, settings

MAX_PROMPTS = 3


def login():
    """Prompt for credentials using the narrow login-only database account."""
    auth_conn = DBUtils.connect_as("AUTH")
    try:
        for _ in range(MAX_PROMPTS):
            user_id = input("User ID: ").strip()
            password = getpass.getpass("Password: ")
            role = LoginService.authenticate(auth_conn, user_id, password)
            if role:
                return user_id, role
            print("Invalid user ID or password.")      # same message for every failure
        return None, None
    finally:
        auth_conn.close()


def main():
    settings.load_env()
    user_id, role = login()
    if role is None:
        print("Too many failed attempts.")
        sys.exit(1)
    view = ViewFactory.get_view(role)
    # Switch to the database account for this role; it can only run this role's procedures.
    conn = DBUtils.connect_as(role, app_user=user_id)
    try:
        print(f"Logged in as {user_id} ({role.lower()})")
        view.run(conn, user_id)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
