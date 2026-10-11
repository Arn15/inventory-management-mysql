"""Connection settings and credentials.

Non-secret settings (host, port, database name) come from config/config.yaml and can be
overridden by environment variables. Secrets (database account passwords) come only from
environment variables, which can be put in a local `.env` file (never committed).
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "config.yaml"

# One database account per application role, plus a narrow account used only for login.
ACCOUNTS = {
    "AUTH": ("inv_auth", "DB_AUTH_PASSWORD"),
    "MANUFACTURER": ("inv_manufacturer", "DB_MANUFACTURER_PASSWORD"),
    "SUPPLIER": ("inv_supplier", "DB_SUPPLIER_PASSWORD"),
    "VIEWER": ("inv_viewer", "DB_VIEWER_PASSWORD"),
}


def load_env() -> None:
    """Load ROOT/.env into the environment if python-dotenv is available (env vars win)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(ROOT / ".env", override=False)


def _config_section(name: str) -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH) as f:
        return (yaml.safe_load(f) or {}).get(name, {}) or {}


def db_settings() -> dict:
    cfg = _config_section("database")
    return {
        "host": os.environ.get("DB_HOST", cfg.get("host", "127.0.0.1")),
        "port": int(os.environ.get("DB_PORT", cfg.get("port", 3306))),
        "database": os.environ.get("DB_NAME", cfg.get("database", "InventoryManagement")),
    }


def account_credentials(key: str) -> tuple[str, str]:
    """(username, password) for an application database account."""
    if key not in ACCOUNTS:
        raise PermissionError(f"No database account for role {key!r}")
    user, env_var = ACCOUNTS[key]
    password = os.environ.get(env_var)
    if not password:
        raise RuntimeError(f"{env_var} is not set (see .env.example)")
    return user, password


def admin_credentials() -> tuple[str, str]:
    """Administrative account used only by manage.py (schema setup, user admin)."""
    password = os.environ.get("DB_ADMIN_PASSWORD")
    if password is None:
        raise RuntimeError("DB_ADMIN_PASSWORD is not set (see .env.example)")
    return os.environ.get("DB_ADMIN_USER", "root"), password


def account_host() -> str:
    """Host part for the application accounts ('%' = any host, e.g. the app container)."""
    return os.environ.get("DB_ACCOUNT_HOST", "%")
