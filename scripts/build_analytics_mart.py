#!/usr/bin/env python3
"""Build the Phase 2.5 analytical mart in a separate SQLite database."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_analysis import iter_statements

BUILD_SQL = PROJECT_ROOT / "sql" / "marts" / "001_build_analytics_mart.sql"
VALIDATE_SQL = PROJECT_ROOT / "sql" / "marts" / "002_validate_analytics_mart.sql"


def build_analytics_mart(source: Path, target: Path) -> list[dict]:
    source = source.resolve()
    target = target.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"source database not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp")
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("ATTACH DATABASE ? AS source", (source.as_uri() + "?mode=ro",))
        connection.executescript(BUILD_SQL.read_text(encoding="utf-8"))
        checks = []
        for statement in iter_statements(VALIDATE_SQL.read_text(encoding="utf-8")):
            row = dict(connection.execute(statement).fetchone())
            checks.append(row)
            if row["violations"] != 0:
                raise RuntimeError(f"mart validation failed: {row}")
        connection.commit()
        connection.execute("DETACH DATABASE source")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"mart integrity check failed: {integrity}")
    except Exception:
        connection.close()
        if temporary.exists():
            temporary.unlink()
        raise
    else:
        connection.close()
        os.replace(temporary, target)
        return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist.sqlite")
    parser.add_argument("--target", type=Path, default=PROJECT_ROOT / "data" / "processed" / "olist_analytics.sqlite")
    args = parser.parse_args()
    checks = build_analytics_mart(args.source, args.target)
    print(f"Built {args.target} with {len(checks)} passing validation checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
