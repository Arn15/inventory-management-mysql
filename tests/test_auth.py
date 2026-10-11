import pytest

from conftest import TEST_PASSWORD
from factory import ViewFactory
from service import LoginService


def _reset(admin, user_id):
    cur = admin.cursor()
    cur.execute("UPDATE User SET failed_attempts = 0, locked_until = NULL WHERE user_id = %s", (user_id,))
    admin.commit()
    cur.close()


def test_correct_password_returns_role(connect, admin):
    _reset(admin, "MFG001")
    assert LoginService.authenticate(connect("AUTH"), "MFG001", TEST_PASSWORD) == "MANUFACTURER"


def test_wrong_password_and_unknown_user_are_rejected(connect, admin):
    _reset(admin, "SUP020")
    auth = connect("AUTH")
    assert LoginService.authenticate(auth, "SUP020", "not-the-password") is None
    assert LoginService.authenticate(auth, "NOSUCHUSER", TEST_PASSWORD) is None
    assert LoginService.authenticate(auth, "", "") is None


def test_lockout_after_five_failures_blocks_correct_password(connect, admin):
    _reset(admin, "SUP021")
    auth = connect("AUTH")
    for _ in range(LoginService.MAX_FAILED_ATTEMPTS):
        assert LoginService.authenticate(auth, "SUP021", "wrong-password") is None
    assert LoginService.authenticate(auth, "SUP021", TEST_PASSWORD) is None   # locked
    _reset(admin, "SUP021")                                                      # admin unlock
    assert LoginService.authenticate(auth, "SUP021", TEST_PASSWORD) == "SUPPLIER"


def test_success_resets_failure_counter(connect, admin):
    _reset(admin, "VIEW001")
    auth = connect("AUTH")
    for _ in range(LoginService.MAX_FAILED_ATTEMPTS - 1):
        LoginService.authenticate(auth, "VIEW001", "wrong-password")
    assert LoginService.authenticate(auth, "VIEW001", TEST_PASSWORD) == "VIEWER"
    for _ in range(LoginService.MAX_FAILED_ATTEMPTS - 1):
        LoginService.authenticate(auth, "VIEW001", "wrong-password")
    assert LoginService.authenticate(auth, "VIEW001", TEST_PASSWORD) == "VIEWER"   # not locked


def test_user_without_password_cannot_log_in(connect, admin):
    cur = admin.cursor()
    cur.execute("UPDATE User SET password_hash = NULL WHERE user_id = 'MFG002'")
    admin.commit()
    assert LoginService.authenticate(connect("AUTH"), "MFG002", "") is None
    assert LoginService.authenticate(connect("AUTH"), "MFG002", TEST_PASSWORD) is None


def test_login_attempts_are_audited(connect, admin):
    _reset(admin, "MFG001")
    LoginService.authenticate(connect("AUTH"), "MFG001", "wrong-password")
    cur = admin.cursor()
    cur.execute("SELECT action, db_account FROM Audit_Log WHERE app_user = 'MFG001' ORDER BY audit_id DESC LIMIT 1")
    action, account = cur.fetchone()
    assert action == "LOGIN_FAILED" and account.startswith("inv_auth@")


def test_unknown_role_gets_no_view():
    with pytest.raises(PermissionError):
        ViewFactory.get_view(None)
    with pytest.raises(PermissionError):
        ViewFactory.get_view("ADMIN")
