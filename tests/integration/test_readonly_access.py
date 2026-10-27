"""Proves guardrail layer 1 against real databases.

Needs `make up && make load`. Skipped automatically when there is no .env or
the databases are not running, for example in CI.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError, OperationalError

from analyst.data.connections import readonly_urls


@pytest.fixture(params=["postgres", "mariadb"])
def readonly_conn(request):
    try:
        url = readonly_urls()[request.param]
    except KeyError:
        pytest.skip("no .env file (run make setup)")
    engine = create_engine(url)
    try:
        conn = engine.connect()
    except OperationalError:
        pytest.skip(f"{request.param} is not reachable (run make up && make load)")
    yield conn
    conn.close()
    engine.dispose()


def test_readonly_account_can_read(readonly_conn):
    count = readonly_conn.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
    assert count == 99_441


@pytest.mark.parametrize(
    "statement",
    [
        "DELETE FROM orders",
        "DROP TABLE orders",
        "UPDATE orders SET order_status = 'hacked'",
        "INSERT INTO sellers (seller_id) VALUES ('x')",
        "CREATE TABLE hacked (id INTEGER)",
    ],
)
def test_readonly_account_cannot_write(readonly_conn, statement):
    with pytest.raises(DBAPIError):
        readonly_conn.execute(text(statement))
