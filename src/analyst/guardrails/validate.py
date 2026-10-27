"""Guardrail layer 2: only let read-only SQL through.

The SQL is parsed into a syntax tree with sqlglot and the tree is inspected.
Searching the raw text for words like "DROP" is not enough: it misses tricks
and wrongly blocks harmless strings such as SELECT 'drop shipping'.

Pure function: no database, no LLM. Fully testable in CI.
"""

from dataclasses import dataclass

import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

# The whole statement must be one of these.
ALLOWED_ROOTS = (exp.Select, exp.SetOperation)  # SetOperation: UNION, INTERSECT, EXCEPT

# None of these may appear anywhere in the tree, not even inside a CTE.
FORBIDDEN_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Merge,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.TruncateTable,
    exp.Grant,
    exp.Copy,
    exp.Command,  # anything sqlglot could not understand, e.g. DO $$ ... $$
    exp.Into,  # SELECT ... INTO new_table creates a table in Postgres
    exp.Lock,  # SELECT ... FOR UPDATE takes write locks
    exp.Set,
)

# Functions that read files, stop other sessions, change settings or stall the
# server. The read-only account and the timeout also stop most of these;
# blocking them here gives a clear reason instead of a database error.
FORBIDDEN_FUNCTIONS = {
    "pg_sleep",
    "sleep",
    "benchmark",
    "pg_terminate_backend",
    "pg_cancel_backend",
    "pg_read_file",
    "pg_read_binary_file",
    "pg_ls_dir",
    "lo_import",
    "lo_export",
    "set_config",
    "dblink",
    "load_file",
}


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str = ""


def _function_name(node: exp.Func) -> str:
    if isinstance(node, exp.Anonymous):
        return node.name.lower()
    return node.sql_name().lower()


def validate_sql(sql: str, dialect: str = "postgres") -> Verdict:
    """Decide whether one SQL string is safe to run."""
    if not sql.strip():
        return Verdict(False, "empty query")

    try:
        statements = [s for s in sqlglot.parse(sql, read=dialect) if s is not None]
    except ParseError as error:
        return Verdict(False, f"could not parse SQL: {error}")

    if len(statements) != 1:
        return Verdict(False, f"expected exactly 1 statement, got {len(statements)}")

    root = statements[0]
    if not isinstance(root, ALLOWED_ROOTS):
        return Verdict(False, f"only SELECT is allowed, got {root.key.upper()}")

    for node in root.walk():
        if isinstance(node, FORBIDDEN_NODES):
            return Verdict(False, f"forbidden operation inside query: {node.key.upper()}")
        if isinstance(node, exp.Func) and _function_name(node) in FORBIDDEN_FUNCTIONS:
            return Verdict(False, f"forbidden function: {_function_name(node)}")

    return Verdict(True)
