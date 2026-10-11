"""Integration tests run against a real MySQL/MariaDB server.

They need the credentials in .env (see .env.example) and RESET the database by running
`manage.py init-db`. Never point them at a database you care about.
"""
import os
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from utils import DBUtils, settings  # noqa: E402

settings.load_env()
TEST_PASSWORD = "Test-Password-2026"


def _db_available() -> bool:
    try:
        DBUtils.connect_admin(database=None).close()
        return True
    except Exception:
        return False


requires_db = pytest.mark.skipif(not _db_available(), reason="no database reachable with .env credentials")


@pytest.fixture(scope="session")
def fresh_db():
    if not _db_available():
        pytest.skip("no database reachable with .env credentials")
    os.environ["DEMO_USER_PASSWORD"] = TEST_PASSWORD
    import manage
    manage.cmd_init_db(None)
    return True


@pytest.fixture
def admin(fresh_db):
    conn = DBUtils.connect_admin()
    yield conn
    conn.close()


@pytest.fixture
def connect(fresh_db):
    opened = []

    def _connect(role, app_user=None):
        c = DBUtils.connect_as(role, app_user=app_user)
        opened.append(c)
        return c
    yield _connect
    for c in opened:
        c.close()
