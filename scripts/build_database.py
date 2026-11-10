#!/usr/bin/env python3
"""Command-line entry point for the Olist SQLite build."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ingest import IngestionError, build_database  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Olist analytical SQLite database")
    parser.add_argument("--raw-dir", type=Path, default=PROJECT_ROOT / "data" / "raw")
    parser.add_argument("--database", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist.sqlite")
    args = parser.parse_args()
    try:
        counts = build_database(args.raw_dir, args.database)
    except IngestionError as exc:
        parser.exit(2, f"Ingestion failed: {exc}\n")
    print(json.dumps({"database": str(args.database), "row_counts": counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
