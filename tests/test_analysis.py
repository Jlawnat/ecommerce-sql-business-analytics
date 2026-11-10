import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.run_analysis import iter_statements
from src.ingest import PROJECT_ROOT, build_database
from tests.fixtures import write_fixture


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        root = Path(cls.temp_dir.name)
        raw_dir = root / "raw"
        write_fixture(raw_dir)
        cls.database = root / "olist.sqlite"
        build_database(raw_dir, cls.database)
        cls.connection = sqlite3.connect(cls.database)
        cls.connection.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()
        cls.temp_dir.cleanup()

    def run_query_file(self, filename):
        sql = (PROJECT_ROOT / "sql" / "analysis" / filename).read_text(encoding="utf-8")
        statements = list(iter_statements(sql))
        self.assertEqual(len(statements), 1)
        return self.connection.execute(statements[0]).fetchall()

    def test_monthly_merchandise_value_excludes_freight_canceled_and_fanout(self):
        rows = self.run_query_file("01_monthly_merchandise_value.sql")
        self.assertEqual([(r["purchase_month"], r["delivered_orders"], r["merchandise_value"]) for r in rows], [
            ("2017-01", 1, 150.0),
            ("2017-02", 1, 200.0),
        ])
        self.assertAlmostEqual(rows[1]["merchandise_value_mom_pct"], 33.33, places=2)
        self.assertEqual(sum(r["merchandise_value"] for r in rows), 350.0)

    def test_category_window_shares_reconcile_to_delivered_merchandise(self):
        rows = self.run_query_file("02_category_sales_concentration.sql")
        self.assertEqual([(r["category"], r["merchandise_value"]) for r in rows], [
            ("category_a", 300.0),
            ("category_b", 50.0),
        ])
        self.assertAlmostEqual(sum(r["merchandise_share_pct"] for r in rows), 100.0, places=2)
        self.assertEqual(rows[-1]["cumulative_share_pct"], 100.0)

    def test_review_analysis_aggregates_multiple_reviews_before_join(self):
        rows = self.run_query_file("03_late_delivery_review_scores.sql")
        result = {r["delivery_timing"]: dict(r) for r in rows}
        self.assertEqual(result["late"]["delivered_orders"], 1)
        self.assertEqual(result["late"]["reviewed_orders"], 1)
        self.assertEqual(result["late"]["avg_review_score"], 2.0)
        self.assertEqual(result["on_time_or_early"]["avg_review_score"], 5.0)

    def test_low_review_share_excludes_orders_without_reviews_from_denominator(self):
        self.connection.execute(
            """INSERT INTO orders VALUES (
                'o4', 'c3', 'delivered', '2017-03-01 00:00:00', '2017-03-01 01:00:00',
                '2017-03-02 00:00:00', '2017-03-12 00:00:00', '2017-03-10 00:00:00'
            )"""
        )
        try:
            rows = self.run_query_file("03_late_delivery_review_scores.sql")
            late = next(row for row in rows if row["delivery_timing"] == "late")
            self.assertEqual(late["delivered_orders"], 2)
            self.assertEqual(late["reviewed_orders"], 1)
            self.assertEqual(late["low_review_share_pct"], 100.0)
        finally:
            self.connection.execute("DELETE FROM orders WHERE order_id = 'o4'")
            self.connection.commit()

    def test_quality_sql_runs_and_exposes_naive_join_inflation(self):
        sql = (PROJECT_ROOT / "sql" / "analysis" / "00_data_quality.sql").read_text(encoding="utf-8")
        result_sets = [self.connection.execute(statement).fetchall() for statement in iter_statements(sql)]
        self.assertGreaterEqual(len(result_sets), 8)
        fanout = result_sets[6][0]
        self.assertGreater(fanout["naive_join_rows"], fanout["source_item_rows"])

    def test_kpi_summary_reconciles_repeat_customers_and_review_distribution(self):
        sql = (PROJECT_ROOT / "sql" / "analysis" / "04_kpi_summary.sql").read_text(encoding="utf-8")
        result_sets = [self.connection.execute(statement).fetchall() for statement in iter_statements(sql)]
        self.assertEqual(len(result_sets), 2)
        summary = result_sets[0][0]
        self.assertEqual(summary["delivered_orders"], 2)
        self.assertEqual(summary["delivered_orders_with_items"], 2)
        self.assertEqual(summary["merchandise_value"], 350.0)
        self.assertEqual(summary["unique_delivered_customers"], 1)
        self.assertEqual(summary["repeat_customers"], 1)
        self.assertEqual(summary["repeat_customer_share_pct"], 100.0)
        self.assertEqual(summary["reviewed_delivered_orders"], 2)
        self.assertEqual(
            [(row["review_score"], row["review_records"]) for row in result_sets[1]],
            [(1, 1), (3, 1), (5, 1)],
        )
        self.assertAlmostEqual(
            sum(row["review_record_share_pct"] for row in result_sets[1]), 100.0, places=1
        )


if __name__ == "__main__":
    unittest.main()
