import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.phase2_analysis import (
    mean_difference_inference,
    stratified_cmh,
    two_proportion_inference,
    wilson_interval,
)
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

    def run_query_results(self, filename):
        sql = (PROJECT_ROOT / "sql" / "analysis" / filename).read_text(encoding="utf-8")
        return [self.connection.execute(statement).fetchall() for statement in iter_statements(sql)]

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

    def test_cohort_identity_retention_value_and_censoring(self):
        self.connection.execute(
            """INSERT INTO orders VALUES (
                'o4', 'c3', 'delivered', '2017-02-15 00:00:00', '2017-02-15 01:00:00',
                '2017-02-16 00:00:00', '2017-02-20 00:00:00', '2017-02-22 00:00:00'
            )"""
        )
        self.connection.execute(
            "INSERT INTO order_items VALUES ('o4', 1, 'p2', 's1', '2017-02-16 00:00:00', 25.0, 2.0)"
        )
        try:
            summary, heatmap = self.run_query_results("05_customer_cohort_retention.sql")
            january = next(row for row in summary if row["cohort_month"] == "2017-01-01")
            february = next(row for row in summary if row["cohort_month"] == "2017-02-01")
            self.assertEqual(january["acquired_customers"], 1)  # c1/c2 share unique id u1
            self.assertEqual(january["repeat_customers"], 1)
            self.assertEqual(january["cohort_merchandise_value"], 350.0)
            self.assertEqual(january["retention_m1_pct"], 100.0)
            self.assertIsNone(january["retention_m2_pct"])
            self.assertEqual(february["acquired_customers"], 1)
            censored = next(r for r in heatmap if r["cohort_month"] == "2017-02-01" and r["month_number"] == 1)
            self.assertEqual(censored["is_observed"], 0)
            self.assertIsNone(censored["retained_customers"])
            self.assertIsNone(censored["retention_rate_pct"])
        finally:
            self.connection.execute("DELETE FROM order_items WHERE order_id = 'o4'")
            self.connection.execute("DELETE FROM orders WHERE order_id = 'o4'")
            self.connection.commit()

    def test_rfm_cutoff_monetary_reconciliation_and_ties(self):
        self.connection.execute("INSERT INTO customers VALUES ('c4', 'u3', 3000, 'niteroi', 'RJ')")
        orders = [
            ("o4", "c3", "2018-08-01 00:00:00", 40.0),
            ("o5", "c4", "2018-08-01 00:00:00", 40.0),
            ("o6", "c4", "2018-09-02 00:00:00", 999.0),
        ]
        for order_id, customer_id, purchase_ts, price in orders:
            self.connection.execute(
                "INSERT INTO orders VALUES (?, ?, 'delivered', ?, ?, ?, ?, ?)",
                (order_id, customer_id, purchase_ts, purchase_ts, purchase_ts, purchase_ts, purchase_ts),
            )
            self.connection.execute(
                "INSERT INTO order_items VALUES (?, 1, 'p2', 's1', ?, ?, 0.0)",
                (order_id, purchase_ts, price),
            )
        try:
            customers, segments = self.run_query_results("06_rfm_segmentation.sql")
            by_id = {row["customer_unique_id"]: row for row in customers}
            self.assertEqual(by_id["u1"]["frequency_orders"], 2)
            self.assertEqual(by_id["u1"]["monetary_value"], 350.0)
            self.assertEqual(by_id["u2"]["f_score"], by_id["u3"]["f_score"])
            self.assertEqual(by_id["u2"]["f_score"], 1)
            self.assertEqual(by_id["u3"]["frequency_orders"], 1)  # post-cutoff o6 excluded
            self.assertEqual(by_id["u3"]["monetary_value"], 40.0)
            self.assertAlmostEqual(sum(row["merchandise_value"] for row in segments), 430.0)
        finally:
            for order_id, _, _, _ in orders:
                self.connection.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
                self.connection.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
            self.connection.execute("DELETE FROM customers WHERE customer_id = 'c4'")
            self.connection.commit()

    def test_sales_trends_pareto_and_boundary_flags(self):
        monthly, pareto, mix = self.run_query_results("07_sales_category_trends.sql")
        self.assertEqual(sum(row["merchandise_value"] for row in monthly), 350.0)
        self.assertEqual(monthly[0]["observation_status"], "incomplete_first_month")
        self.assertEqual(monthly[-1]["observation_status"], "incomplete_last_month")
        self.assertAlmostEqual(monthly[1]["raw_merchandise_value_mom_pct"], 33.33, places=2)
        self.assertIsNone(monthly[1]["interpretable_mom_pct"])
        self.assertEqual(pareto[-1]["cumulative_share_pct"], 100.0)
        self.assertAlmostEqual(sum(row["merchandise_value"] for row in pareto), 350.0)
        self.assertEqual(len(mix), 4)  # two months x two categories, including zero cells
        self.assertTrue(all(row["interpretable_share_change_pp"] is None for row in mix))

    def test_delivery_analysis_preserves_order_grain_and_attribution(self):
        coverage, timing, states, categories, strata = self.run_query_results("08_delivery_segment_analysis.sql")
        self.assertEqual(coverage[0]["delivered_orders"], 2)
        self.assertEqual(coverage[0]["timing_eligible_orders"], 2)
        self.assertEqual(coverage[0]["inference_eligible_orders"], 2)
        by_timing = {row["delivery_timing"]: row for row in timing}
        self.assertEqual(by_timing["late"]["reviewed_orders"], 1)
        self.assertEqual(by_timing["late"]["avg_review_score"], 2.0)  # two reviews averaged first
        category_a = next(row for row in categories if row["attributed_category"] == "category_a")
        self.assertEqual(category_a["timing_eligible_orders"], 2)
        self.assertEqual(category_a["mixed_category_orders"], 1)
        self.assertEqual(sum(row["timing_eligible_orders"] for row in categories), 2)
        self.assertEqual(sum(row["late_reviewed_orders"] + row["on_time_reviewed_orders"] for row in strata), 2)

    def test_statistical_helpers_are_deterministic(self):
        lo, hi = wilson_interval(50, 100)
        self.assertAlmostEqual(lo, 0.4038, places=4)
        self.assertAlmostEqual(hi, 0.5962, places=4)
        proportions = two_proportion_inference(50, 100, 30, 100)
        self.assertAlmostEqual(proportions["difference"], 0.2)
        self.assertLess(proportions["p_value"], 0.01)
        means = mean_difference_inference(100, 3.0, 10.0, 100, 4.0, 17.0)
        self.assertAlmostEqual(means["difference"], -1.0)
        self.assertLess(means["p_value"], 0.001)
        cmh = stratified_cmh([
            {"late_reviewed_orders": 10, "late_low_review_orders": 5, "on_time_reviewed_orders": 20, "on_time_low_review_orders": 2},
            {"late_reviewed_orders": 20, "late_low_review_orders": 8, "on_time_reviewed_orders": 30, "on_time_low_review_orders": 3},
        ])
        self.assertGreater(cmh["common_odds_ratio"], 1.0)
        self.assertLess(cmh["p_value"], 0.05)


if __name__ == "__main__":
    unittest.main()
