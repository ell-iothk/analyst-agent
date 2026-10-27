"""Guardrail layer 2. No database, no LLM."""

import pytest

from analyst.guardrails.validate import validate_sql

SAFE = [
    "SELECT COUNT(*) FROM orders",
    "SELECT COUNT(*) FROM orders;",
    "select order_status, count(*) from orders group by order_status",
    "WITH monthly AS (SELECT order_id FROM orders) SELECT COUNT(*) FROM monthly",
    "SELECT customer_state FROM customers UNION SELECT seller_state FROM sellers",
    # Comments are not code. The DROP below never runs.
    "SELECT 1 -- DROP TABLE orders",
    "SELECT 1 /* ; DROP TABLE orders */",
    # A dangerous-looking text inside a string literal is just data.
    "SELECT '; DROP TABLE orders; --' AS note",
    "SELECT product_category_name FROM products WHERE product_category_name = 'drop'",
]

DANGEROUS = [
    # From the design document, stage 1 gate
    "SELECT 1; DROP TABLE orders",
    "SELECT 1; DELETE FROM orders; --",
    # Plain write and admin statements
    "DROP TABLE orders",
    "DELETE FROM orders",
    "UPDATE orders SET order_status = 'x'",
    "INSERT INTO sellers (seller_id) VALUES ('x')",
    "TRUNCATE orders",
    "ALTER TABLE orders ADD COLUMN x INT",
    "CREATE TABLE hacked (id INT)",
    "GRANT ALL ON orders TO PUBLIC",
    "COPY orders TO '/tmp/orders.csv'",
    "SET statement_timeout = 0",
    # Disguised as SELECT
    "WITH d AS (DELETE FROM orders RETURNING *) SELECT * FROM d",
    "SELECT * INTO hacked FROM orders",
    "SELECT * FROM orders FOR UPDATE",
    "SELECT pg_sleep(600)",
    "SELECT pg_read_file('/etc/passwd')",
    # Not understood by the parser
    "DO $$ BEGIN DROP TABLE orders; END $$",
    "VACUUM",
    # Broken or empty
    "SELEC * FROM orders",
    "",
    "   ",
]


@pytest.mark.parametrize("sql", SAFE)
def test_safe_queries_are_allowed(sql):
    verdict = validate_sql(sql)
    assert verdict.allowed, verdict.reason


@pytest.mark.parametrize("sql", DANGEROUS)
def test_dangerous_queries_are_rejected(sql):
    verdict = validate_sql(sql)
    assert not verdict.allowed
    assert verdict.reason


def test_rejection_explains_why():
    verdict = validate_sql("SELECT 1; DROP TABLE orders")
    assert verdict.reason == "expected exactly 1 statement, got 2"


def naive_keyword_check(sql: str) -> bool:
    """What NOT to do: search the text for bad words."""
    return "drop" not in sql.lower()


def test_keyword_search_is_not_enough():
    harmless = "SELECT '; DROP TABLE orders; --' AS note"
    disguised = "WITH d AS (DELETE FROM orders RETURNING *) SELECT * FROM d"

    # The naive check gets both wrong...
    assert naive_keyword_check(harmless) is False
    assert naive_keyword_check(disguised) is True
    # ...the syntax tree gets both right.
    assert validate_sql(harmless).allowed
    assert not validate_sql(disguised).allowed
