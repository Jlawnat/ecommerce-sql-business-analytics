"""Streamlit AppTest smoke coverage for every published route."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


class DashboardSmokeTests(unittest.TestCase):
    def assert_starts(self, relative_path: str):
        app = AppTest.from_file(ROOT / relative_path, default_timeout=20).run()
        self.assertEqual(list(app.exception), [], f"Uncaught exception in {relative_path}")
        self.assertGreater(len(app.title), 0, f"No title rendered in {relative_path}")

    def test_multipage_entrypoint_starts(self):
        self.assert_starts("app/streamlit_app.py")

    def test_entrypoint_bootstraps_project_root_for_direct_streamlit_launch(self):
        source = (ROOT / "app/streamlit_app.py").read_text(encoding="utf-8")
        self.assertLess(source.index("sys.path.insert"), source.index("from dashboard.ui"))

    def test_every_page_bootstraps_project_root_for_cold_deep_links(self):
        for path in sorted((ROOT / "app/views").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(page=path.name):
                self.assertIn("parents[2]", source)
                self.assertLess(source.index("sys.path.insert"), source.index("from dashboard"))

    def test_each_analytical_page_starts(self):
        for path in sorted((ROOT / "app/views").glob("*.py")):
            with self.subTest(page=path.name):
                self.assert_starts(str(path.relative_to(ROOT)))

    def test_page_sources_do_not_reference_customer_level_exports(self):
        forbidden = ("rfm_customers.csv", "delivery_model_population.csv")
        text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "app").rglob("*.py"))
        for token in forbidden:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
