"""Olist table definitions, portable across Postgres and MariaDB.

Table names drop the "olist_" prefix and "_dataset" suffix from the source files.
Column names are kept exactly as in the source, typos included
(for example "product_name_lenght").
"""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
)

# Olist IDs are always 32-character hex strings.
ID = String(32)
# Brazilian ZIP prefixes: 5 digits, often with a leading zero. Stored as text
# because an integer column would turn "01310" into 1310.
ZIP = String(5)
# Money in Brazilian reais with 2 decimals. Numeric, not float, so sums are exact.
MONEY = Numeric(10, 2)

metadata = MetaData()

customers = Table(
    "customers",
    metadata,
    Column("customer_id", ID, primary_key=True),
    Column("customer_unique_id", ID, nullable=False),
    Column("customer_zip_code_prefix", ZIP),
    Column("customer_city", String(64)),
    Column("customer_state", String(2)),
)

sellers = Table(
    "sellers",
    metadata,
    Column("seller_id", ID, primary_key=True),
    Column("seller_zip_code_prefix", ZIP),
    Column("seller_city", String(64)),
    Column("seller_state", String(2)),
)

product_category_name_translation = Table(
    "product_category_name_translation",
    metadata,
    Column("product_category_name", String(64), primary_key=True),
    Column("product_category_name_english", String(64)),
)

# No foreign key to product_category_name_translation: two categories in the
# source data ("pc_gamer" and "portateis_cozinha_e_preparadores_de_alimentos")
# have no translation, so the constraint would reject real rows.
products = Table(
    "products",
    metadata,
    Column("product_id", ID, primary_key=True),
    Column("product_category_name", String(64)),
    Column("product_name_lenght", Integer),
    Column("product_description_lenght", Integer),
    Column("product_photos_qty", Integer),
    Column("product_weight_g", Integer),
    Column("product_length_cm", Integer),
    Column("product_height_cm", Integer),
    Column("product_width_cm", Integer),
)

orders = Table(
    "orders",
    metadata,
    Column("order_id", ID, primary_key=True),
    Column("customer_id", ID, ForeignKey("customers.customer_id"), nullable=False),
    Column("order_status", String(16), nullable=False),
    Column("order_purchase_timestamp", DateTime, nullable=False),
    Column("order_approved_at", DateTime),
    Column("order_delivered_carrier_date", DateTime),
    Column("order_delivered_customer_date", DateTime),
    Column("order_estimated_delivery_date", DateTime),
)

order_items = Table(
    "order_items",
    metadata,
    Column("order_id", ID, ForeignKey("orders.order_id"), primary_key=True),
    Column("order_item_id", Integer, primary_key=True),
    Column("product_id", ID, ForeignKey("products.product_id"), nullable=False),
    Column("seller_id", ID, ForeignKey("sellers.seller_id"), nullable=False),
    Column("shipping_limit_date", DateTime),
    Column("price", MONEY, nullable=False),
    Column("freight_value", MONEY, nullable=False),
)

order_payments = Table(
    "order_payments",
    metadata,
    Column("order_id", ID, ForeignKey("orders.order_id"), primary_key=True),
    Column("payment_sequential", Integer, primary_key=True),
    Column("payment_type", String(16)),
    Column("payment_installments", Integer),
    Column("payment_value", MONEY, nullable=False),
)

# review_id alone is not unique in the source (99,224 rows, 98,410 distinct ids),
# so the primary key is (review_id, order_id).
order_reviews = Table(
    "order_reviews",
    metadata,
    Column("review_id", ID, primary_key=True),
    Column("order_id", ID, ForeignKey("orders.order_id"), primary_key=True),
    Column("review_score", Integer, nullable=False),
    Column("review_comment_title", String(64)),
    Column("review_comment_message", Text),
    Column("review_creation_date", DateTime),
    Column("review_answer_timestamp", DateTime),
)
