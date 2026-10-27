"""Database connection URLs, built from .env.

Three kinds of account, each with the least power it needs:
- setup: creates accounts (Postgres admin, MariaDB root)
- admin: creates tables and loads data
- readonly: what the agent uses; can only read
"""

import os

from dotenv import load_dotenv
from sqlalchemy import URL


def _urls(user: str, password: str) -> dict[str, URL]:
    load_dotenv()
    common = {
        "username": user,
        "password": password,
        "host": "localhost",
        "database": os.environ["DB_NAME"],
    }
    return {
        "postgres": URL.create(
            "postgresql+psycopg", port=int(os.environ["POSTGRES_PORT"]), **common
        ),
        "mariadb": URL.create(
            "mysql+pymysql",
            port=int(os.environ["MARIADB_PORT"]),
            query={"charset": "utf8mb4"},
            **common,
        ),
    }


def admin_urls() -> dict[str, URL]:
    load_dotenv()
    return _urls(os.environ["DB_ADMIN_USER"], os.environ["DB_ADMIN_PASSWORD"])


def readonly_urls() -> dict[str, URL]:
    load_dotenv()
    return _urls(os.environ["DB_READONLY_USER"], os.environ["DB_READONLY_PASSWORD"])


def setup_urls() -> dict[str, URL]:
    """Accounts allowed to create other accounts."""
    load_dotenv()
    admin = admin_urls()
    root = _urls("root", os.environ["DB_ROOT_PASSWORD"])
    # In the Postgres image the admin is a superuser. In MariaDB only root can
    # create users; the admin only owns the olist database.
    return {"postgres": admin["postgres"], "mariadb": root["mariadb"]}
