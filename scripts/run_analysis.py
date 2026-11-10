#!/usr/bin/env python3
"""Execute checked-in analysis SQL and print each result set."""

import argparse
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = (
    "00_data_quality.sql",
    "01_monthly_merchandise_value.sql",
    "02_category_sales_concentration.sql",
    "03_late_delivery_review_scores.sql",
    "04_kpi_summary.sql",
)


def iter_statements(sql_text: str):
    buffer = ""
    for line in sql_text.splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            if buffer.strip().strip(";"):
                yield buffer
            buffer = ""
    if buffer.strip():
        raise ValueError("Incomplete SQL statement")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Olist quality checks and Phase 1 analyses")
    parser.add_argument("--database", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist.sqlite")
    parser.add_argument("--query", choices=DEFAULT_FILES, action="append")
    args = parser.parse_args()
    if not args.database.is_file():
        parser.error(f"database not found: {args.database}; run scripts/build_database.py first")

    connection = sqlite3.connect(f"file:{args.database}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        for filename in args.query or DEFAULT_FILES:
            path = PROJECT_ROOT / "sql" / "analysis" / filename
            print(f"\n## {filename}")
            for number, statement in enumerate(iter_statements(path.read_text(encoding="utf-8")), start=1):
                rows = connection.execute(statement).fetchall()
                print(f"\nResult {number}")
                if not rows:
                    print("(no rows)")
                    continue
                columns = rows[0].keys()
                print(" | ".join(columns))
                for row in rows:
                    print(" | ".join("NULL" if row[column] is None else str(row[column]) for column in columns))
    finally:
        connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
