"""Create the read-only database account the agent uses.

Guardrail layer 1 from the design: even if the agent is tricked into running
DROP TABLE, the database itself refuses, because this account can only read.
Safe to run many times.
"""

import os
import re

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from analyst.data.connections import setup_urls

# Names and passwords go straight into SQL (CREATE USER cannot take bound
# parameters), so only allow characters that cannot break out of the statement.
SAFE_NAME = re.compile(r"^[a-z_][a-z0-9_]{0,30}$")
SAFE_PASSWORD = re.compile(r"^[A-Za-z0-9_.!@#%^*+=-]{8,64}$")


def check_safe(user: str, password: str) -> None:
    if not SAFE_NAME.match(user):
        raise ValueError(f"Unsafe user name {user!r}: use lowercase letters, digits, _")
    if not SAFE_PASSWORD.match(password):
        raise ValueError(
            "Unsafe read-only password: use 8-64 letters, digits or _.!@#%^*+=- "
            "(no quotes, spaces or backslashes)"
        )


def postgres_statements(user: str, password: str, database: str) -> list[str]:
    return [
        f"ALTER ROLE {user} LOGIN PASSWORD '{password}'",
        # Layer 1b: every transaction of this role starts read-only.
        f"ALTER ROLE {user} SET default_transaction_read_only = on",
        f"GRANT CONNECT ON DATABASE {database} TO {user}",
        f"GRANT USAGE ON SCHEMA public TO {user}",
        f"GRANT SELECT ON ALL TABLES IN SCHEMA public TO {user}",
        # Tables are dropped and recreated by `make load`; grant on future ones too.
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {user}",
    ]


def mariadb_statements(user: str, password: str, database: str) -> list[str]:
    return [
        f"CREATE USER IF NOT EXISTS '{user}'@'%' IDENTIFIED BY '{password}'",
        f"ALTER USER '{user}'@'%' IDENTIFIED BY '{password}'",
        f"GRANT SELECT ON {database}.* TO '{user}'@'%'",
    ]


def main() -> None:
    load_dotenv()
    user = os.environ["DB_READONLY_USER"]
    password = os.environ["DB_READONLY_PASSWORD"]
    database = os.environ["DB_NAME"]
    check_safe(user, password)

    urls = setup_urls()

    with create_engine(urls["postgres"]).begin() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :name"), {"name": user}
        ).first()
        if not exists:
            conn.execute(text(f"CREATE ROLE {user}"))
        for statement in postgres_statements(user, password, database):
            conn.execute(text(statement))
    print(f"postgres: read-only account '{user}' ready")

    with create_engine(urls["mariadb"]).begin() as conn:
        for statement in mariadb_statements(user, password, database):
            conn.execute(text(statement))
    print(f"mariadb:  read-only account '{user}' ready")


if __name__ == "__main__":
    main()
