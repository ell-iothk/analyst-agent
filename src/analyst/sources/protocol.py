"""Data source contract.

The agent only knows this contract, not which database sits behind it.
If the agent ever needs to know which engine is in use, this contract is wrong.
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    nullable: bool = True


@dataclass(frozen=True)
class TableSchema:
    name: str
    columns: tuple[Column, ...]

    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]


@dataclass(frozen=True)
class Schema:
    tables: tuple[TableSchema, ...]

    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]

    def find(self, name: str) -> TableSchema | None:
        for t in self.tables:
            if t.name == name:
                return t
        return None


@dataclass(frozen=True)
class QueryResult:
    """Result of executing a query."""

    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]

    @property
    def row_count(self) -> int:
        return len(self.rows)


@runtime_checkable
class DataSource(Protocol):
    def dialect(self) -> str:
        """Query language, for example "sql:postgres" or "sql:mysql"."""
        ...

    def schema(self) -> Schema:
        """Available tables and columns."""
        ...

    def capabilities(self) -> set[str]:
        """What the source supports, for example {"aggregation", "join", "time_range", "top_n"}."""
        ...

    def execute(self, query: str) -> QueryResult:
        """Run a query and return its result."""
        ...
