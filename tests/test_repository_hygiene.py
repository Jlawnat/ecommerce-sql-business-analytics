import json
import re
import struct
import tempfile
import unittest
from pathlib import Path

from scripts.check_repository import (
    check_markdown_links,
    check_markdown_structure,
    check_mermaid_blocks,
    check_privacy_paths,
    check_readme_screenshots,
)


ROOT = Path(__file__).resolve().parents[1]


class RepositoryHygieneTests(unittest.TestCase):
    def test_readme_claims_match_published_evidence(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        phase1 = (ROOT / "reports/PHASE1_RESULTS.md").read_text(encoding="utf-8")
        count_section = phase1.split("## Database and verified counts", 1)[1].split("## ", 1)[0]
        source_counts = [int(value.replace(",", "")) for value in re.findall(r"\| `[^`]+` \| ([\d,]+) \|", count_section)]
        self.assertEqual(sum(source_counts), 1_550_922)
        self.assertIn("1,550,922", readme)

        executive = json.loads((ROOT / "web/public/data/executive-overview.json").read_text(encoding="utf-8"))
        customer = json.loads((ROOT / "web/public/data/customer-intelligence.json").read_text(encoding="utf-8"))
        delivery = json.loads((ROOT / "web/public/data/delivery-satisfaction.json").read_text(encoding="utf-8"))
        self.assertIn(f'{executive["summary"]["deliveredOrders"]:,}', readme)
        self.assertIn(f'{executive["summary"]["merchandiseValue"]:,.2f}', readme)
        self.assertIn(f'{customer["summary"]["observedCustomers"]:,}', readme)
        self.assertIn(f'{delivery["primaryModel"]["oddsRatio"]:.2f}', readme)
        self.assertIn(f'{delivery["primaryModel"]["riskDifference"] * 100:+.2f}', readme)

    def test_markdown_links_report_missing_relative_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[missing](docs/missing.md)\n", encoding="utf-8")
            errors = check_markdown_links(root, [root / "README.md"])
        self.assertEqual(len(errors), 1)
        self.assertIn("docs/missing.md", errors[0])

    def test_markdown_links_accept_existing_targets_and_headings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[guide](docs/guide.md#run-tests)\n", encoding="utf-8")
            (root / "docs").mkdir()
            guide = root / "docs/guide.md"
            guide.write_text("# Guide\n\n## Run tests\n", encoding="utf-8")
            errors = check_markdown_links(root, [root / "README.md", guide])
        self.assertEqual(errors, [])

    def test_mermaid_blocks_require_supported_header_and_closure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "diagram.md"
            malformed.write_text("```mermaid\nA --> B\n", encoding="utf-8")
            errors = check_mermaid_blocks([malformed])
        self.assertTrue(any("unclosed" in error.lower() for error in errors))

    def test_markdown_structure_requires_one_title_and_closed_fences(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "guide.md"
            document.write_text("## Missing title\n\n```bash\necho incomplete\n", encoding="utf-8")
            errors = check_markdown_structure([document])
        self.assertEqual(len(errors), 2)

    def test_privacy_paths_reject_generated_and_raw_assets(self):
        paths = [
            "web/.next/server/app.js",
            "web/node_modules/react/index.js",
            "data/raw/olist_orders_dataset.csv",
            "data/processed/olist.sqlite",
            ".env",
        ]
        errors = check_privacy_paths(paths)
        self.assertEqual(len(errors), len(paths))

    def test_readme_screenshot_must_be_tracked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = "visualizations/screenshots/v2/example.png"
            screenshot = root / target
            screenshot.parent.mkdir(parents=True)
            screenshot.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 1024, 900))
            (root / "README.md").write_text(f"![Example]({target})\n", encoding="utf-8")

            errors = check_readme_screenshots(root, tracked_paths=set())

        self.assertEqual(errors, [f"README.md: screenshot is not tracked by Git: {target}"])


if __name__ == "__main__":
    unittest.main()
