"""Least-privilege enforcement by the database itself."""
import datetime as dt

import mysql.connector
import pytest

from security.privileges import ROLE_GRANTS

ERR = mysql.connector.Error


def _fails(conn, sql, params=None):
    cur = conn.cursor()
    with pytest.raises(ERR):
        cur.execute(sql, params or ())
        cur.fetchall()
    cur.close()


def _call(conn, proc, args):
    cur = conn.cursor()
    cur.callproc(proc, args)
    rows = [r.fetchall() for r in cur.stored_results()]  # noqa: deprecated alias, still supported
    conn.commit()
    cur.close()
    return rows


@pytest.mark.parametrize("role", list(ROLE_GRANTS))
def test_role_can_read_its_tables(connect, role):
    conn = connect(role)
    cur = conn.cursor()
    for table in ROLE_GRANTS[role]["tables"]:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")
        cur.fetchall()
    cur.close()


@pytest.mark.parametrize("role", list(ROLE_GRANTS))
def test_role_cannot_write_tables_or_read_users(connect, role):
    conn = connect(role)
    _fails(conn, "SELECT password_hash FROM User")
    _fails(conn, "SELECT * FROM Audit_Log")
    _fails(conn, "INSERT INTO Category (category_name) VALUES ('x')")
    _fails(conn, "UPDATE Ingredient_Inventory SET remaining_amt = 0")
    _fails(conn, "DELETE FROM Products")
    _fails(conn, "DROP TABLE Products")


def test_roles_cannot_run_other_roles_procedures(connect):
    _fails(connect("VIEWER"), "CALL CreateProduct(101, 2, 'x', 100, '[]')")
    _fails(connect("SUPPLIER"), "CALL CreateProductBatch(101, 100, 1, 100)")
    _fails(connect("MANUFACTURER"), "CALL CreateIngredientBatch(20, 101, 0.1, 100, '2099-01-01')")
    _fails(connect("VIEWER"), "CALL TraceRecall('I106-S20-B2')")


def test_auth_account_is_limited_to_login_columns(connect):
    auth = connect("AUTH")
    _fails(auth, "SELECT first_name FROM User")
    _fails(auth, "UPDATE User SET role_code = 'MANUFACTURER' WHERE user_id = 'VIEW001'")
    _fails(auth, "UPDATE User SET password_hash = 'x' WHERE user_id = 'VIEW001'")
    _fails(auth, "SELECT * FROM Products")


def test_viewer_procedures_run(connect):
    v = connect("VIEWER")
    assert _call(v, "BrowseProductTypes", [])[0]
    assert _call(v, "GetSupplierSpendByManufacturer", [101]) is not None
    assert _call(v, "GenerateIngredientList", ["P100-M101-B1"])[0]


def test_manufacturer_procedures_run(connect):
    m = connect("MANUFACTURER")
    assert _call(m, "get_prod_on_hand", [101, 100]) is not None
    assert _call(m, "almost_expired_ing", [365]) is not None
    assert _call(m, "TraceRecall", ["I106-S20-B2"]) is not None


def test_supplier_write_is_audited_with_app_user(connect, admin):
    s = connect("SUPPLIER", app_user="SUP020")
    expiry = dt.date.today() + dt.timedelta(days=120)
    _call(s, "CreateIngredientBatch", [20, 101, 0.1, 100, expiry])
    cur = admin.cursor()
    cur.execute("SELECT app_user, db_account, action, table_name FROM Audit_Log "
                "WHERE table_name = 'Ingredient_Inventory' ORDER BY audit_id DESC LIMIT 1")
    app_user, account, action, table = cur.fetchone()
    assert (app_user, action) == ("SUP020", "INSERT") and account.startswith("inv_supplier@")


def test_business_rule_still_enforced_through_procedure(connect):
    s = connect("SUPPLIER", app_user="SUP020")
    with pytest.raises(ERR, match="failed"):   # the 90-day expiry trigger fires; the procedure re-raises it generically
        _call(s, "CreateIngredientBatch", [20, 101, 0.1, 100, dt.date.today() + dt.timedelta(days=30)])


def test_audit_log_is_append_only_even_for_admin(admin):
    _fails(admin, "UPDATE Audit_Log SET action = 'X'")
    _fails(admin, "DELETE FROM Audit_Log")
