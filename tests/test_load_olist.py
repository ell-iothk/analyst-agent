import gzip
from datetime import datetime
from decimal import Decimal

from analyst.data.load_olist import EXPECTED_ROWS, SOURCE_FILES, convert, read_rows
from analyst.data.olist_schema import metadata, order_items


def test_every_table_has_a_source_file_and_expected_count():
    assert set(SOURCE_FILES) == set(metadata.tables)
    assert set(EXPECTED_ROWS) == set(metadata.tables)


def test_empty_text_becomes_null():
    assert convert("", order_items.c.price.type) is None


def test_values_are_converted_to_column_types():
    assert convert("3", order_items.c.order_item_id.type) == 3
    assert convert("58.90", order_items.c.price.type) == Decimal("58.90")
    assert convert("2017-09-19 09:45:35", order_items.c.shipping_limit_date.type) == datetime(
        2017, 9, 19, 9, 45, 35
    )


def test_zip_prefix_keeps_its_leading_zero():
    column = metadata.tables["customers"].c.customer_zip_code_prefix
    assert convert("01310", column.type) == "01310"


def test_byte_order_mark_is_removed_from_header(tmp_path):
    path = tmp_path / "translation.csv.gz"
    with gzip.open(path, "wt", encoding="utf-8-sig") as f:
        f.write("product_category_name,product_category_name_english\nartes,art\n")

    table = metadata.tables["product_category_name_translation"]
    rows = list(read_rows(path, table))

    assert rows == [{"product_category_name": "artes", "product_category_name_english": "art"}]
