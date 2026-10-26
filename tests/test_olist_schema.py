import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy.schema import CreateTable

from analyst.data.olist_schema import metadata

EXPECTED_TABLES = {
    "customers",
    "sellers",
    "products",
    "product_category_name_translation",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
}


def test_all_eight_tables_are_defined():
    assert set(metadata.tables) == EXPECTED_TABLES


@pytest.mark.parametrize(
    "dialect", [postgresql.dialect(), mysql.dialect()], ids=["postgres", "mysql"]
)
def test_ddl_compiles_for_both_engines(dialect):
    for table in metadata.sorted_tables:
        CreateTable(table).compile(dialect=dialect)


def test_tables_can_be_created_in_a_real_database():
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES


def test_review_primary_key_is_composite():
    pk = [c.name for c in metadata.tables["order_reviews"].primary_key]
    assert pk == ["review_id", "order_id"]


def test_zip_prefix_is_text_to_keep_leading_zeros():
    column = metadata.tables["customers"].c.customer_zip_code_prefix
    assert column.type.python_type is str
