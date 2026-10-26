"""Download raw Olist data into data/raw/olist/.

Source: Brazilian E-Commerce Public Dataset by Olist (CC BY-NC-SA 4.0),
via a GitHub mirror pinned to one commit so the files never change.
"""

import urllib.request
from pathlib import Path

COMMIT = "6e7f3d9b614655007f94dda9063ac3d5fb14fed9"  # pragma: allowlist secret
BASE_URL = f"https://raw.githubusercontent.com/infobarbosa/dataset-olist/{COMMIT}/data"

OLIST_FILES = [
    "olist_orders_dataset.csv.gz",
    "olist_order_items_dataset.csv.gz",
    "olist_order_payments_dataset.csv.gz",
    "olist_order_reviews_dataset.csv.gz",
    "olist_customers_dataset.csv.gz",
    "olist_sellers_dataset.csv.gz",
    "olist_products_dataset.csv.gz",
    "product_category_name_translation.csv.gz",
]

TARGET_DIR = Path("data/raw/olist")


def download(name: str, folder: Path) -> Path:
    """Download one file into folder. Skip it if it already exists."""
    target = folder / name
    if target.exists():
        print(f"skip      {name} (already exists)")
        return target

    # Download to a .part file first. If the download is interrupted,
    # a half-written file is never mistaken for a complete one.
    partial = folder / f"{name}.part"
    urllib.request.urlretrieve(f"{BASE_URL}/{name}", partial)
    partial.rename(target)
    print(f"download  {name}")
    return target


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for name in OLIST_FILES:
        download(name, TARGET_DIR)
    print(f"Done. {len(OLIST_FILES)} files in {TARGET_DIR}/")


if __name__ == "__main__":
    main()
