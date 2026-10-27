"""Load raw Olist CSV files into Postgres and MariaDB.

Run `make data` first. Uses the admin account from .env, because loading needs
write access. The agent itself will use a separate read-only account.
"""

import csv
import gzip
import sys
from collections.abc import Iterator
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import (
    URL,
    DateTime,
    Engine,
    Integer,
    Numeric,
    Table,
    create_engine,
    func,
    select,
)

from analyst.data.connections import admin_urls
from analyst.data.olist_schema import metadata

RAW_DIR = Path("data/raw/olist")
BATCH_SIZE = 5_000

# Which raw file feeds which table.
SOURCE_FILES = {
    "customers": "olist_customers_dataset.csv.gz",
    "sellers": "olist_sellers_dataset.csv.gz",
    "product_category_name_translation": "product_category_name_translation.csv.gz",
    "products": "olist_products_dataset.csv.gz",
    "orders": "olist_orders_dataset.csv.gz",
    "order_items": "olist_order_items_dataset.csv.gz",
    "order_payments": "olist_order_payments_dataset.csv.gz",
    "order_reviews": "olist_order_reviews_dataset.csv.gz",
}

# Row counts of the source files. Loading fails loudly if any table differs.
EXPECTED_ROWS = {
    "customers": 99_441,
    "sellers": 3_095,
    "product_category_name_translation": 71,
    "products": 32_951,
    "orders": 99_441,
    "order_items": 112_650,
    "order_payments": 103_886,
    "order_reviews": 99_224,
}


def convert(value: str, column_type) -> object:
    """Turn one CSV text value into the Python type the column expects."""
    if value == "":
        return None
    if isinstance(column_type, Integer):
        return int(value)
    if isinstance(column_type, Numeric):
        return Decimal(value)
    if isinstance(column_type, DateTime):
        return datetime.fromisoformat(value)
    return value


def read_rows(path: Path, table: Table) -> Iterator[dict]:
    """Yield one dict per CSV row, with values converted to the column types."""
    # utf-8-sig drops the invisible byte order mark some files start with.
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            yield {name: convert(value, table.c[name].type) for name, value in row.items()}


def load_table(engine: Engine, table: Table, path: Path) -> int:
    """Insert all rows of one file into one table, in batches. Return the row count."""
    batch = []
    with engine.begin() as conn:
        for row in read_rows(path, table):
            batch.append(row)
            if len(batch) == BATCH_SIZE:
                conn.execute(table.insert(), batch)
                batch = []
        if batch:
            conn.execute(table.insert(), batch)
        return conn.execute(select(func.count()).select_from(table)).scalar_one()


def load_into(engine_name: str, url: URL) -> None:
    engine = create_engine(url)
    print(f"\n== {engine_name}")
    metadata.drop_all(engine)
    metadata.create_all(engine)
    # sorted_tables puts parents (customers) before children (orders).
    for table in metadata.sorted_tables:
        count = load_table(engine, table, RAW_DIR / SOURCE_FILES[table.name])
        expected = EXPECTED_ROWS[table.name]
        status = "ok" if count == expected else f"MISMATCH, expected {expected:,}"
        print(f"  {table.name:<36} {count:>8,}  {status}")
        if count != expected:
            sys.exit(f"{engine_name}: {table.name} has {count} rows, expected {expected}")
    engine.dispose()


def main() -> None:
    for engine_name, url in admin_urls().items():
        load_into(engine_name, url)
    print("\nDone. Both databases hold identical Olist data.")


if __name__ == "__main__":
    main()
