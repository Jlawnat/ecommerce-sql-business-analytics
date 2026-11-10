import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.ingest import IngestionError, build_database, validate_source_files
from src.olist_config import EXPECTED_FILENAMES
from tests.fixtures import ROWS, write_fixture


class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.raw_dir = self.root / "raw"
        self.database = self.root / "olist.sqlite"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_manifest_has_exact_nine_source_files(self):
        self.assertEqual(len(EXPECTED_FILENAMES), 9)
        self.assertEqual(
            set(EXPECTED_FILENAMES),
            {
                "olist_customers_dataset.csv",
                "olist_geolocation_dataset.csv",
                "olist_order_items_dataset.csv",
                "olist_order_payments_dataset.csv",
                "olist_order_reviews_dataset.csv",
                "olist_orders_dataset.csv",
                "olist_products_dataset.csv",
                "olist_sellers_dataset.csv",
                "product_category_name_translation.csv",
            },
        )

    def test_missing_files_are_all_reported(self):
        self.raw_dir.mkdir()
        with self.assertRaises(IngestionError) as raised:
            validate_source_files(self.raw_dir)
        self.assertIn("olist_orders_dataset.csv", str(raised.exception))
        self.assertIn("product_category_name_translation.csv", str(raised.exception))

    def test_loads_all_tables_preserves_grains_and_parses_nulls(self):
        write_fixture(self.raw_dir)
        counts = build_database(self.raw_dir, self.database)
        self.assertEqual(counts, {table: len(rows) for table, rows in ROWS.items()})
        connection = sqlite3.connect(self.database)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM order_items").fetchone()[0], 4)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM geolocation").fetchone()[0], 2)
            self.assertEqual(
                connection.execute("SELECT order_purchase_timestamp FROM orders WHERE order_id='o1'").fetchone()[0],
                "2017-01-01 10:00:00",
            )
            self.assertIsNone(
                connection.execute("SELECT order_approved_at FROM orders WHERE order_id='o3'").fetchone()[0]
            )
            self.assertIsNone(
                connection.execute("SELECT product_weight_g FROM products WHERE product_id='p2'").fetchone()[0]
            )
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            connection.close()

    def test_duplicate_composite_key_fails_without_replacing_good_database(self):
        write_fixture(self.raw_dir)
        build_database(self.raw_dir, self.database)
        item_file = self.raw_dir / "olist_order_items_dataset.csv"
        with item_file.open("a", encoding="utf-8") as target:
            target.write("o1,1,p1,s1,2017-01-04 00:00:00,1.00,0.00\n")
        with self.assertRaises(IngestionError):
            build_database(self.raw_dir, self.database)
        connection = sqlite3.connect(self.database)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM order_items").fetchone()[0], 4)
        finally:
            connection.close()
        self.assertFalse(self.database.with_name("olist.sqlite.building").exists())

    def test_rerun_is_idempotent(self):
        write_fixture(self.raw_dir)
        first = build_database(self.raw_dir, self.database)
        second = build_database(self.raw_dir, self.database)
        self.assertEqual(first, second)
        connection = sqlite3.connect(self.database)
        try:
            self.assertEqual(connection.execute("SELECT SUM(price) FROM order_items").fetchone()[0], 1349.0)
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
