"""Deterministic chart contracts for the Phase 3 presentation layer."""

import math
import unittest

from dashboard.charts import (
    association_forest,
    category_pareto,
    cohort_heatmap,
    heterogeneity_chart,
    km_curve,
    monthly_trend,
    ranked_late_rates,
    rfm_distribution,
)
from dashboard.data import DashboardRepository


class DashboardChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = DashboardRepository()

    def assert_figure_contract(self, figure, min_traces=1):
        self.assertGreaterEqual(len(figure.data), min_traces)
        self.assertGreaterEqual(figure.layout.height, 240)
        self.assertLessEqual(figure.layout.height, 540)
        self.assertTrue(figure.layout.title.text)
        self.assertEqual(figure.layout.paper_bgcolor, "rgba(0,0,0,0)")

    def test_all_published_figures_have_bounded_dimensions_and_labels(self):
        figures = [
            monthly_trend(self.repo.csv("monthly_sales")),
            category_pareto(self.repo.csv("category_pareto")),
            cohort_heatmap(self.repo.csv("cohort_retention")),
            rfm_distribution(self.repo.csv("rfm_segments")),
            km_curve(self.repo.csv("repeat_km")),
            ranked_late_rates(self.repo.csv("delivery_state"), "customer_state"),
            association_forest(self.repo.csv("delivery_timing"), self.repo.json("research_results")),
            heterogeneity_chart(self.repo.json("research_results")),
        ]
        for figure in figures:
            with self.subTest(title=figure.layout.title.text):
                self.assert_figure_contract(figure)

    def test_cohort_censoring_remains_missing_and_color_scale_excludes_m0(self):
        source = self.repo.csv("cohort_retention")
        figure = cohort_heatmap(source, 12)
        values = figure.data[0].z
        self.assertTrue(any(math.isnan(float(value)) for row in values for value in row if value is not None))
        self.assertLess(figure.data[0].zmax, 100)

    def test_km_chart_includes_estimate_and_confidence_band(self):
        figure = km_curve(self.repo.csv("repeat_km"))
        self.assertEqual(len(figure.data), 3)
        self.assertEqual(figure.data[1].fill, "tonexty")
        self.assertIn("95% CI", figure.data[2].hovertemplate)

    def test_association_chart_uses_log_odds_ratio_axis_and_confidence_intervals(self):
        figure = association_forest(self.repo.csv("delivery_timing"), self.repo.json("research_results"))
        self.assertEqual(figure.layout.xaxis.type, "log")
        self.assertEqual(len(figure.data[0].x), 2)
        self.assertTrue(figure.data[0].error_x.visible is not False)


if __name__ == "__main__":
    unittest.main()

