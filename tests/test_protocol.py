from analyst.sources.protocol import Column, DataSource, QueryResult, Schema, TableSchema


class FakeSource:
    """In-memory data source for tests. No real database."""

    def dialect(self) -> str:
        return "sql:fake"

    def schema(self) -> Schema:
        products = TableSchema(
            name="products",
            columns=(Column("id", "INTEGER", nullable=False), Column("name", "TEXT")),
        )
        return Schema(tables=(products,))

    def capabilities(self) -> set[str]:
        return {"aggregation"}

    def execute(self, query: str) -> QueryResult:
        return QueryResult(columns=("total",), rows=((42,),))


class IncompleteSource:
    """Forgot to implement three methods. Must not count as a DataSource."""

    def dialect(self) -> str:
        return "sql:broken"


def test_complete_source_satisfies_contract():
    assert isinstance(FakeSource(), DataSource)


def test_incomplete_source_is_rejected():
    assert not isinstance(IncompleteSource(), DataSource)


def test_schema_can_be_navigated():
    schema = FakeSource().schema()
    assert schema.table_names() == ["products"]
    assert schema.find("products").column_names() == ["id", "name"]
    assert schema.find("missing") is None


def test_query_result_counts_rows():
    result = FakeSource().execute("SELECT 42")
    assert result.row_count == 1
    assert result.rows[0][0] == 42
