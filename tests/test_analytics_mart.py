import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.build_analytics_mart import build_analytics_mart
from src.ingest import build_database
from tests.fixtures import write_fixture


class AnalyticsMartTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        raw = root / "raw"
        write_fixture(raw)
        self.source = root / "olist.sqlite"
        self.target = root / "olist_analytics.sqlite"
        build_database(raw, self.source)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_mart_grains_relationships_and_reconciliation(self):
        source_size = self.source.stat().st_size
        checks = build_analytics_mart(self.source, self.target)
        self.assertTrue(checks)
        self.assertTrue(all(row["violations"] == 0 for row in checks))
        self.assertEqual(self.source.stat().st_size, source_size)
        connection = sqlite3.connect(self.target)
        connection.row_factory = sqlite3.Row
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mart_delivered_orders").fetchone()[0], 2)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mart_delivered_order_items").fetchone()[0], 3)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mart_customer_snapshot").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM mart_reviewed_orders").fetchone()[0], 2)
            order = connection.execute("SELECT * FROM mart_delivered_orders WHERE order_id = 'o1'").fetchone()
            self.assertEqual(order["merchandise_value"], 150.0)
            self.assertEqual(order["item_count"], 2)
            self.assertEqual(order["seller_count"], 1)
            self.assertEqual(order["category_count"], 2)
            self.assertEqual(order["attributed_category"], "category_a")
            self.assertEqual(order["review_record_count"], 2)
            self.assertEqual(order["review_score"], 2.0)
            customer = connection.execute("SELECT * FROM mart_customer_snapshot").fetchone()
            self.assertEqual(customer["frequency_orders"], 2)
            self.assertEqual(customer["monetary_value"], 350.0)
            self.assertIsNotNone(customer["second_purchase_timestamp"])
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
        finally:
            connection.close()

    def test_mart_rebuild_is_idempotent(self):
        first = build_analytics_mart(self.source, self.target)
        second = build_analytics_mart(self.source, self.target)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
