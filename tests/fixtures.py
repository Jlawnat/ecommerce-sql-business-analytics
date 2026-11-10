"""Small deterministic Olist-shaped fixture; values are test data, not findings."""

import csv
from pathlib import Path

from src.olist_config import CSV_SPECS


ROWS = {
    "customers": [
        ["c1", "u1", "1000", "sao paulo", "SP"],
        ["c2", "u1", "1000", "sao paulo", "SP"],
        ["c3", "u2", "2000", "rio", "RJ"],
    ],
    "geolocation": [
        ["1000", "-23.5", "-46.6", "sao paulo", "SP"],
        ["1000", "-23.5", "-46.6", "sao paulo", "SP"],
    ],
    "products": [
        ["p1", "cat_a", "10", "20", "1", "100", "10", "5", "5"],
        ["p2", "cat_b", "", "", "", "", "", "", ""],
    ],
    "sellers": [
        ["s1", "1000", "sao paulo", "SP"],
    ],
    "category_translation": [
        ["cat_a", "category_a"],
        ["cat_b", "category_b"],
    ],
    "orders": [
        ["o1", "c1", "delivered", "2017-01-01 10:00:00", "2017-01-01 11:00:00", "2017-01-03 09:00:00", "2017-01-11 12:00:00", "2017-01-10 00:00:00"],
        ["o2", "c2", "delivered", "2017-02-01 10:00:00", "2017-02-01 11:00:00", "2017-02-03 09:00:00", "2017-02-08 12:00:00", "2017-02-10 00:00:00"],
        ["o3", "c3", "canceled", "2017-02-05 10:00:00", "", "", "", "2017-02-20 00:00:00"],
    ],
    "order_items": [
        ["o1", "1", "p1", "s1", "2017-01-04 00:00:00", "100.00", "10.00"],
        ["o1", "2", "p2", "s1", "2017-01-04 00:00:00", "50.00", "5.00"],
        ["o2", "1", "p1", "s1", "2017-02-04 00:00:00", "200.00", "20.00"],
        ["o3", "1", "p2", "s1", "2017-02-08 00:00:00", "999.00", "30.00"],
    ],
    "order_payments": [
        ["o1", "1", "credit_card", "1", "100.00"],
        ["o1", "2", "voucher", "1", "65.00"],
        ["o2", "1", "credit_card", "2", "220.00"],
        ["o3", "1", "credit_card", "1", "1029.00"],
    ],
    "order_reviews": [
        ["r1", "o1", "1", "", "late", "2017-01-12 00:00:00", "2017-01-13 00:00:00"],
        ["r1b", "o1", "3", "second", "", "2017-01-12 00:00:00", "2017-01-14 00:00:00"],
        ["r2", "o2", "5", "great", "fast", "2017-02-09 00:00:00", "2017-02-10 00:00:00"],
    ],
}


def write_fixture(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for spec in CSV_SPECS:
        with (raw_dir / spec.filename).open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow(spec.columns)
            writer.writerows(ROWS[spec.table])
