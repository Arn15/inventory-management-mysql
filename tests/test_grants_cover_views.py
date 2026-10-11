"""Static check: every procedure/table a role's screens use is granted to that role's account,
and nothing beyond that. Follows view -> service -> repository calls in the source."""
import ast
import re
from pathlib import Path

from security.privileges import ROLE_GRANTS

SRC = Path(__file__).resolve().parents[1] / "src"
TABLES = ["Category", "Products", "User", "Manufacturer_Product", "Manufacturer", "Supplier_Ingredient",
          "Supplier", "Ingredients", "Ingredient_Inventory", "Product_Inventory",
          "Product_Ingredient_Batch_Mapping", "Recipe", "Do_Not_Combine", "Ingredient_Formulation", "Audit_Log"]
VIEWS = {"MANUFACTURER": "ManufacturerView.py", "SUPPLIER": "SupplierView.py", "VIEWER": "ViewerView.py"}


def _functions(folder):
    out = {}
    for f in (SRC / folder).glob("*.py"):
        src = f.read_text()
        for node in ast.parse(src).body:
            if isinstance(node, ast.FunctionDef):
                out[f"{f.stem}.{node.name}"] = (node, ast.get_source_segment(src, node))
    return out


def _usage(role):
    repos, services = _functions("repository"), _functions("service")
    view_src = (SRC / "view" / VIEWS[role]).read_text()
    procs, tables = set(), set()
    for svc in set(re.findall(r"(\w+Service)\.(\w+)", view_src)):
        _, svc_src = services[".".join(svc)]
        for repo in re.findall(r"(\w+Repository)\.(\w+)", svc_src):
            node, src = repos[".".join(repo)]
            procs |= set(re.findall(r'callproc\(\s*"(\w+)"', src))
            sql = " ".join(n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str))
            tables |= {t for t in TABLES if re.search(rf"\b(FROM|JOIN)\s+{t}\b", sql, re.I)}
    return procs, tables


def test_grants_match_what_each_role_uses():
    for role, grants in ROLE_GRANTS.items():
        procs, tables = _usage(role)
        assert procs == set(grants["procedures"]), f"{role} procedures: used {sorted(procs)}"
        assert tables == set(grants["tables"]), f"{role} tables: used {sorted(tables)}"


def test_no_role_touches_user_or_audit_tables():
    for role, grants in ROLE_GRANTS.items():
        assert "User" not in grants["tables"] and "Audit_Log" not in grants["tables"]


def test_no_eval_or_exec_in_source():
    for f in SRC.rglob("*.py"):
        tree = ast.parse(f.read_text())
        calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert not calls & {"eval", "exec"}, f"{f.name} uses eval/exec"
