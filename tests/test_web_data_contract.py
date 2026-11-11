import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "publish_web_aggregates", ROOT / "scripts/publish_web_aggregates.py"
)
assert SPEC and SPEC.loader
publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publisher)


class WebAggregateContractTests(unittest.TestCase):
    def test_methodology_catalogue_links_only_tracked_safe_evidence(self):
        catalogue = ROOT / "web/lib/methodology-content.ts"
        self.assertTrue(catalogue.exists(), "Methodology evidence catalogue is missing")
        source = catalogue.read_text(encoding="utf-8")
        forbidden = (
            "data/raw/",
            ".sqlite",
            "rfm_customers.csv",
            "delivery_model_population.csv",
        )
        for value in forbidden:
            self.assertNotIn(value, source)

        import re

        linked_paths = set(
            re.findall(
                r'"((?:docs|reports|sql|scripts|tests|web)/[^"?#]+(?:\.md|\.sql|\.py|\.json|\.csv|\.tsx?))"',
                source,
            )
        )
        self.assertGreaterEqual(len(linked_paths), 12)
        for relative_path in linked_paths:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_contract_reconciles_verified_executive_metrics(self):
        payload = publisher.build_contract()
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertEqual(payload["summary"]["deliveredOrders"], 96_478)
        self.assertEqual(payload["summary"]["merchandiseValue"], 13_221_498.11)
        self.assertEqual(payload["summary"]["averageOrderValue"], 137.04)
        self.assertEqual(payload["summary"]["topCategorySharePct"], 9.33)
        self.assertEqual(payload["summary"]["categoriesToReach80Pct"], 18)
        self.assertEqual(payload["summary"]["thresholdCumulativeSharePct"], 81.29)

    def test_contract_is_aggregate_only_and_deterministic(self):
        payload = publisher.build_contract()
        serialized = json.dumps(payload, sort_keys=True)
        for forbidden in ("customer_id", "order_id", "seller_id", "review_id", "sqlite"):
            self.assertNotIn(forbidden, serialized.lower())
        with tempfile.TemporaryDirectory() as directory:
            first = publisher.publish(Path(directory) / "first.json").read_bytes()
            second = publisher.publish(Path(directory) / "second.json").read_bytes()
        self.assertEqual(first, second)

    def test_customer_contract_flags_verified_small_cohort(self):
        payload = publisher.build_customer_contract()
        cell = next(
            row for row in payload["cohorts"]
            if row["cohortMonth"] == "2016-12" and row["monthNumber"] == 1
        )
        self.assertEqual(cell["acquiredCustomers"], 1)
        self.assertEqual(cell["retainedCustomers"], 1)
        self.assertEqual(cell["retentionRatePct"], 100.0)

    def test_delivery_contract_preserves_adjusted_and_observed_anchors(self):
        payload = publisher.build_delivery_contract()
        observed = payload["observedContrast"]
        model = payload["primaryModel"]
        self.assertAlmostEqual(observed["lateRisk"], 0.539877)
        self.assertAlmostEqual(observed["onTimeRisk"], 0.091875)
        self.assertAlmostEqual(model["oddsRatio"], 11.407611357421521)
        self.assertAlmostEqual(model["orCi95Low"], 10.808322680678685)
        self.assertAlmostEqual(model["orCi95High"], 12.04012877174768)
        self.assertAlmostEqual(model["riskDifference"], 0.4249428982461647)
        self.assertEqual(model["reviewedOrders"], 95_824)
        self.assertTrue(model["converged"])

    def test_delivery_contract_exposes_uncertainty_and_aggregate_only_comparisons(self):
        payload = publisher.build_delivery_contract()
        bounds = payload["missingReviewBounds"]
        self.assertAlmostEqual(bounds["worstCaseMinimum"], 0.43169181894739994)
        self.assertAlmostEqual(bounds["worstCaseMaximum"], 0.45820158572133285)
        self.assertEqual({row["includedGroups"] for row in payload["heterogeneity"]}, {20, 22, 34})
        self.assertTrue(all(row["eligibleOrders"] >= 500 for row in payload["comparisons"]["states"]))
        self.assertTrue(all(row["eligibleOrders"] >= 500 for row in payload["comparisons"]["categories"]))
        serialized = json.dumps(payload, sort_keys=True).lower()
        for forbidden in ("customer_id", "order_id", "seller_id", "review_id", "sqlite"):
            self.assertNotIn(forbidden, serialized)
        with tempfile.TemporaryDirectory() as directory:
            first = publisher.publish_delivery(Path(directory) / "first.json").read_bytes()
            second = publisher.publish_delivery(Path(directory) / "second.json").read_bytes()
        self.assertEqual(first, second)

    def test_contract_has_honest_boundary_states_and_ordered_pareto(self):
        payload = publisher.build_contract()
        states = {row["observationStatus"] for row in payload["monthly"]}
        self.assertIn("incomplete_first_month", states)
        self.assertIn("incomplete_last_month", states)
        self.assertIn("sparse_month", states)
        cumulative = [row["cumulativeSharePct"] for row in payload["categories"]]
        self.assertEqual(cumulative, sorted(cumulative))
        self.assertGreaterEqual(cumulative[17], 80)
        self.assertLess(cumulative[16], 80)

    def test_customer_contract_preserves_verified_research_estimates(self):
        payload = publisher.build_customer_contract()
        self.assertEqual(payload["summary"]["observedCustomers"], 93_358)
        self.assertAlmostEqual(payload["summary"]["repeat90"]["repeatIncidence"], 0.021279730139541764)
        self.assertAlmostEqual(payload["summary"]["repeat365"]["repeatIncidence"], 0.038117413841527226)
        self.assertAlmostEqual(payload["summary"]["stability"]["exactAgreement"], 0.5775664239192434)
        self.assertAlmostEqual(payload["summary"]["stability"]["cohenKappa"], 0.42623884288497094)
        self.assertEqual(sum(row["customers"] for row in payload["rfm"]), 93_358)

    def test_customer_contract_keeps_censoring_unavailable_and_is_aggregate_only(self):
        payload = publisher.build_customer_contract()
        censored = [row for row in payload["cohorts"] if not row["observed"]]
        self.assertTrue(censored)
        self.assertTrue(all(row["retainedCustomers"] is None for row in censored))
        self.assertTrue(all(row["retentionRatePct"] is None for row in censored))
        month_zero = [row for row in payload["cohorts"] if row["monthNumber"] == 0]
        self.assertTrue(all(row["retentionRatePct"] == 100.0 for row in month_zero))
        serialized = json.dumps(payload, sort_keys=True).lower()
        for forbidden in ("customer_id", "order_id", "seller_id", "review_id", "sqlite"):
            self.assertNotIn(forbidden, serialized)
        with tempfile.TemporaryDirectory() as directory:
            first = publisher.publish_customer(Path(directory) / "first.json").read_bytes()
            second = publisher.publish_customer(Path(directory) / "second.json").read_bytes()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

