import unittest

from scripts.phase25_research import (
    fit_grouped_logistic,
    heterogeneity,
    kaplan_meier,
    missing_review_bounds,
    rfm_stability,
)


class Phase25StatisticsTests(unittest.TestCase):
    def test_kaplan_meier_handles_events_and_right_censoring(self):
        rows = [
            {"observed_days": 1, "repeat_event": 1},
            {"observed_days": 2, "repeat_event": 1},
            {"observed_days": 3, "repeat_event": 0},
        ]
        estimates = kaplan_meier(rows, [1, 2, 3])
        self.assertAlmostEqual(estimates[0]["repeat_cumulative_incidence"], 1 / 3)
        self.assertAlmostEqual(estimates[1]["repeat_cumulative_incidence"], 2 / 3)
        self.assertAlmostEqual(estimates[2]["repeat_cumulative_incidence"], 2 / 3)
        self.assertLessEqual(estimates[1]["repeat_ci_95_low"], 2 / 3)
        self.assertGreaterEqual(estimates[1]["repeat_ci_95_high"], 2 / 3)

    def test_grouped_logistic_recovers_positive_late_association(self):
        rows = []
        for month in ("2018-01", "2018-02"):
            for late in (0, 1):
                for single in (0, 1):
                    total = 200
                    events = 20 + 60 * late + 5 * single
                    rows.append({"purchase_month": month, "customer_state": "SP", "category_group": "test",
                                 "value_band": "01_under_50", "single_seller": single, "is_late": late,
                                 "reviewed_orders": total, "low_reviews": events, "score_one_reviews": events // 2})
        model = fit_grouped_logistic(rows)
        self.assertTrue(model["converged"])
        self.assertGreater(model["late_odds_ratio"], 1)
        self.assertGreater(model["late_or_ci_95_low"], 1)
        self.assertGreater(model["standardized_risk_difference"], 0)
        self.assertGreater(model["auc"], 0.5)

    def test_missing_review_bounds_contain_observed_difference(self):
        rows = [
            {"is_late": 0, "timing_eligible_orders": 100, "reviewed_orders": 90, "observed_low_reviews": 9},
            {"is_late": 1, "timing_eligible_orders": 50, "reviewed_orders": 40, "observed_low_reviews": 20},
        ]
        result = missing_review_bounds(rows)
        self.assertLessEqual(result["worst_case_minimum"], result["observed_risk_difference"])
        self.assertGreaterEqual(result["worst_case_maximum"], result["observed_risk_difference"])

    def test_heterogeneity_and_rfm_stability_are_reproducible(self):
        subgroups = [
            {"subgroup_type": "state", "subgroup_value": "A", "late_reviewed": 100, "late_low": 50, "on_time_reviewed": 200, "on_time_low": 20},
            {"subgroup_type": "state", "subgroup_value": "B", "late_reviewed": 100, "late_low": 20, "on_time_reviewed": 200, "on_time_low": 30},
        ]
        result = heterogeneity(subgroups, "state")
        self.assertEqual(result["included_groups"], 2)
        self.assertGreaterEqual(result["p_value"], 0)
        self.assertLessEqual(result["p_value"], 1)
        rfm = [
            {"cutoff": "a", "customer_unique_id": "1", "rfm_segment": "x"},
            {"cutoff": "a", "customer_unique_id": "2", "rfm_segment": "y"},
            {"cutoff": "b", "customer_unique_id": "1", "rfm_segment": "x"},
            {"cutoff": "b", "customer_unique_id": "2", "rfm_segment": "x"},
        ]
        stability = rfm_stability(rfm)
        self.assertEqual(stability["common_customers"], 2)
        self.assertEqual(stability["exact_segment_agreement"], 0.5)


if __name__ == "__main__":
    unittest.main()
