import csv
import json
import sqlite3
import unittest
from pathlib import Path

from scripts.phase2_analysis import mean_difference_inference, two_proportion_inference
from src.ingest import PROJECT_ROOT


class Phase25RealDataAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = PROJECT_ROOT / "data" / "processed" / "olist.sqlite"
        if not cls.database.is_file():
            raise unittest.SkipTest("real Olist database is not available")
        cls.connection = sqlite3.connect(cls.database)
        cls.connection.row_factory = sqlite3.Row

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "connection"):
            cls.connection.close()

    @staticmethod
    def csv_rows(filename):
        with (PROJECT_ROOT / "reports" / "phase2_outputs" / filename).open(encoding="utf-8") as source:
            return list(csv.DictReader(source))

    def test_published_population_and_monetary_anchors_reproduce_independently(self):
        row = self.connection.execute(
            """SELECT COUNT(DISTINCT o.order_id) AS orders,
                      COUNT(DISTINCT c.customer_unique_id) AS customers,
                      ROUND(SUM(i.price), 2) AS merchandise
               FROM orders AS o JOIN customers AS c USING(customer_id)
               JOIN order_items AS i USING(order_id)
               WHERE o.order_status = 'delivered'"""
        ).fetchone()
        # Distinct protects order count from item fan-out; value is valid at item grain.
        self.assertEqual(row["orders"], 96478)
        self.assertEqual(row["customers"], 93358)
        self.assertEqual(row["merchandise"], 13221498.11)
        cohort = self.csv_rows("cohort_summary.csv")
        self.assertEqual(sum(int(r["acquired_customers"]) for r in cohort), 93358)
        self.assertAlmostEqual(sum(float(r["cohort_merchandise_value"]) for r in cohort), 13221498.11, places=2)

    def test_rfm_cutoff_and_output_reconcile_without_temporal_leakage(self):
        rfm = self.csv_rows("rfm_customers.csv")
        self.assertEqual(len(rfm), 93358)
        self.assertTrue(all(row["analysis_cutoff"] == "2018-09-01 00:00:00" for row in rfm))
        source_value = self.connection.execute(
            """SELECT ROUND(SUM(i.price), 2) FROM order_items AS i JOIN orders AS o USING(order_id)
               WHERE o.order_status = 'delivered' AND datetime(o.order_purchase_timestamp) < datetime('2018-09-01 00:00:00')"""
        ).fetchone()[0]
        self.assertAlmostEqual(sum(float(row["monetary_value"]) for row in rfm), source_value, places=2)
        self.assertEqual(
            self.connection.execute("SELECT COUNT(*) FROM orders WHERE order_status='delivered' AND datetime(order_purchase_timestamp) >= datetime('2018-09-01')").fetchone()[0],
            0,
        )

    def test_delivery_statistics_reproduce_from_order_grain(self):
        rows = self.connection.execute(
            """WITH review AS (
                   SELECT order_id, AVG(review_score) AS score FROM order_reviews
                   WHERE review_score IS NOT NULL GROUP BY order_id
               )
               SELECT datetime(o.order_delivered_customer_date) > datetime(o.order_estimated_delivery_date) AS late,
                      COUNT(*) AS n, AVG(r.score) AS mean_score, AVG(r.score*r.score) AS mean_square,
                      SUM(r.score <= 2) AS low
               FROM orders AS o JOIN review AS r USING(order_id)
               WHERE o.order_status='delivered' AND o.order_delivered_customer_date IS NOT NULL
                 AND o.order_estimated_delivery_date IS NOT NULL GROUP BY late ORDER BY late"""
        ).fetchall()
        ontime, late = rows
        mean_result = mean_difference_inference(late["n"], late["mean_score"], late["mean_square"],
                                                ontime["n"], ontime["mean_score"], ontime["mean_square"])
        proportion_result = two_proportion_inference(late["low"], late["n"], ontime["low"], ontime["n"])
        published = json.loads((PROJECT_ROOT / "reports" / "phase2_outputs" / "statistical_results.json").read_text())
        self.assertAlmostEqual(mean_result["difference"], published["review_score_mean_difference_late_minus_on_time"]["difference"], places=5)
        self.assertAlmostEqual(proportion_result["difference"], published["low_review_share_difference_late_minus_on_time"]["difference"], places=12)
        self.assertEqual(late["n"] + ontime["n"], 95824)

    def test_phase25_models_converged_and_preserved_phase2_sample(self):
        result_path = PROJECT_ROOT / "reports" / "phase25_outputs" / "research_results.json"
        if not result_path.is_file():
            self.skipTest("Phase 2.5 outputs have not been generated")
        delivery = json.loads(result_path.read_text())["delivery_satisfaction"]
        for name in ("primary_adjusted_model", "single_seller_sensitivity", "score_one_sensitivity"):
            self.assertTrue(delivery[name]["converged"])
        self.assertEqual(delivery["primary_adjusted_model"]["reviewed_orders"], 95824)


if __name__ == "__main__":
    unittest.main()
