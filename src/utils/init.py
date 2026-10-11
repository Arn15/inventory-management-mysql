"""Run the SQL scripts that create the schema, procedures, triggers and seed data."""
from __future__ import annotations

from pathlib import Path

from utils import settings

# (script, statement delimiter), in execution order
SCRIPTS = [
    ("data/ddl-tables.sql", ";"),
    ("data/ddl-procedures.sql", "$$"),
    ("data/ddl-triggers.sql", "//"),
    ("data/ddl-audit.sql", "//"),
    ("data/dml-initialise.sql", ";"),
]


def run_sql_script(conn, path: Path, delimiter: str = ";") -> None:
    """Execute a script split on its DELIMITER. Raises on the first failing statement."""
    sql = path.read_text()
    sql = sql.replace("DELIMITER " + delimiter, "").replace("DELIMITER ;", "")
    statements = [s.strip() for s in sql.split(delimiter) if s.strip()]
    cursor = conn.cursor()
    try:
        for stmt in statements:
            cursor.execute(stmt)
            if cursor.with_rows:
                cursor.fetchall()
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"{path.name}: {e}\n--- statement ---\n{stmt[:300]}") from e
    finally:
        cursor.close()
    print(f"  applied {path.name}")


def create_schema(conn) -> None:
    for script, delim in SCRIPTS:
        run_sql_script(conn, settings.ROOT / script, delim)
