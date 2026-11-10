import tempfile
import unittest
from pathlib import Path

from dashboard.data import (
    ASSETS,
    EXPORT_ALLOWLIST,
    DashboardRepository,
    DataUnavailable,
    PROJECT_ROOT,
)


class DashboardDataContractTests(unittest.TestCase):
    def test_authoritative_anchor_metrics_match_verified_outputs(self):
        metrics = DashboardRepository(PROJECT_ROOT).anchor_metrics()
        self.assertEqual(metrics["delivered_orders"], 96478)
        self.assertEqual(metrics["merchandise_value"], 13221498.11)
        self.assertEqual(metrics["average_order_value"], 137.04)
        self.assertEqual(metrics["top_category"], "health_beauty")
        self.assertEqual(metrics["top_category_share_pct"], 9.33)
        self.assertEqual(metrics["inference_eligible_orders"], 95824)

    def test_all_checked_in_assets_satisfy_declared_columns(self):
        repository = DashboardRepository(PROJECT_ROOT)
        for key, contract in ASSETS.items():
            if contract.path.endswith(".csv"):
                frame = repository.csv(key)
                self.assertTrue(set(contract.required_columns).issubset(frame.columns), key)
            else:
                self.assertIsInstance(repository.json(key), dict)

    def test_missing_outputs_have_actionable_empty_state(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = DashboardRepository(Path(directory))
            with self.assertRaises(DataUnavailable) as context:
                repository.csv("monthly_sales")
            self.assertIn("phase2_analysis.py", str(context.exception))
            self.assertFalse(any(repository.availability().values()))

    def test_export_allowlist_excludes_customer_level_and_model_population(self):
        self.assertNotIn("rfm_customers", EXPORT_ALLOWLIST)
        self.assertNotIn("delivery_model_population", EXPORT_ALLOWLIST)
        self.assertTrue(all(key in ASSETS for key in EXPORT_ALLOWLIST))
        with self.assertRaises(PermissionError):
            DashboardRepository(PROJECT_ROOT).export_csv("research_results")


if __name__ == "__main__":
    unittest.main()
