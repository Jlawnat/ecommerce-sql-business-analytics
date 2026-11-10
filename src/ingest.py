"""Transactional CSV-to-SQLite loader for the nine Olist source files."""

from __future__ import annotations

import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from src.olist_config import CSV_SPECS, CsvSpec


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema" / "001_create_tables.sql"


class IngestionError(RuntimeError):
    """Raised when source files do not satisfy the documented contract."""


def validate_source_files(raw_dir: Path) -> None:
    missing = [spec.filename for spec in CSV_SPECS if not (raw_dir / spec.filename).is_file()]
    if missing:
        raise IngestionError("Missing required Olist CSV file(s): " + ", ".join(missing))


def _parse_timestamp(value: str, column: str, filename: str, row_number: int) -> str | None:
    if not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError as exc:
        raise IngestionError(
            f"Invalid timestamp in {filename}, row {row_number}, column {column}: {value!r}"
        ) from exc
    return parsed.isoformat(sep=" ")


def _convert(value: str | None, column: str, spec: CsvSpec, row_number: int):
    if value is None:
        raise IngestionError(f"Missing column {column!r} in {spec.filename}")
    if column in spec.timestamp_columns:
        return _parse_timestamp(value, column, spec.filename, row_number)
    if not value.strip():
        return None
    try:
        if column in spec.integer_columns:
            return int(float(value))
        if column in spec.real_columns:
            return float(value)
    except ValueError as exc:
        raise IngestionError(
            f"Invalid numeric value in {spec.filename}, row {row_number}, column {column}: {value!r}"
        ) from exc
    return value


def _load_csv(connection: sqlite3.Connection, raw_dir: Path, spec: CsvSpec) -> int:
    path = raw_dir / spec.filename
    insert_columns = (("source_row_number",) if spec.add_source_row_number else ()) + spec.columns
    placeholders = ", ".join("?" for _ in insert_columns)
    sql = f"INSERT INTO {spec.table} ({', '.join(insert_columns)}) VALUES ({placeholders})"
    count = 0
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        actual = tuple(reader.fieldnames or ())
        missing_columns = [column for column in spec.columns if column not in actual]
        if missing_columns:
            raise IngestionError(
                f"{spec.filename} is missing column(s): {', '.join(missing_columns)}"
            )
        for source_row_number, row in enumerate(reader, start=1):
            values = [_convert(row.get(column), column, spec, source_row_number + 1) for column in spec.columns]
            if spec.add_source_row_number:
                values.insert(0, source_row_number)
            try:
                connection.execute(sql, values)
            except sqlite3.IntegrityError as exc:
                raise IngestionError(
                    f"Integrity error loading {spec.filename} at CSV row {source_row_number + 1}: {exc}"
                ) from exc
            count += 1
    return count


def build_database(raw_dir: Path, database_path: Path) -> dict[str, int]:
    """Build a fresh database beside the target and atomically replace it on success."""
    raw_dir = Path(raw_dir)
    database_path = Path(database_path)
    validate_source_files(raw_dir)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    staging_path = database_path.with_name(database_path.name + ".building")
    if staging_path.exists():
        staging_path.unlink()

    counts: dict[str, int] = {}
    connection = sqlite3.connect(staging_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        with connection:
            # Parent tables precede child tables regardless of manifest order.
            load_order = (
                "customers", "geolocation", "products", "sellers", "category_translation",
                "orders", "order_items", "order_payments", "order_reviews",
            )
            by_table = {spec.table: spec for spec in CSV_SPECS}
            for table in load_order:
                counts[table] = _load_csv(connection, raw_dir, by_table[table])
            violations = connection.execute("PRAGMA foreign_key_check").fetchall()
            if violations:
                raise IngestionError(f"Foreign-key violations after load: {violations[:10]}")
        connection.execute("PRAGMA optimize")
    except Exception:
        connection.close()
        if staging_path.exists():
            staging_path.unlink()
        raise
    else:
        connection.close()
        os.replace(staging_path, database_path)
    return counts
