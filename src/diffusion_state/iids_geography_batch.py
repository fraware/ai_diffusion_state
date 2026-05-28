"""Per-batch geography export validation, concat, and SQLite-backed normalization."""
from __future__ import annotations

import csv
import re
import sqlite3
import tempfile
from pathlib import Path

from diffusion_state.iids_geo_join import (
    KEY_COVERAGE_MIN_RATE,
    MIN_CITY_FILL,
    MIN_PROVINCE_FILL,
    _join_keys_from_row,
    _non_empty_str,
    evaluate_geography_acceptance,
    production_key_coverage_thresholds,
    summarize_geography_from_counts,
)
from diffusion_state.iids_geo_stream import (
    _pick_geo_field,
    iter_geography_rows,
    measure_geography_key_coverage,
)
from diffusion_state.iids_geography_normalize import CONTRACT_COLUMNS

BATCH_NUM_RE = re.compile(r"(\d{3})\s*$")
EXPORT_DIR_DEFAULT_NAME = "iids_geo_exports"
KEY_BATCH_GLOB = "iids_geo_keys_batch_*.csv"
EXPORT_BATCH_GLOB = "iids_geo_export_batch_*.csv"


def _batch_number(path: Path) -> str | None:
    match = BATCH_NUM_RE.search(path.stem)
    return match.group(1) if match else None


def list_key_batches(batch_dir: Path) -> list[Path]:
    return sorted(batch_dir.glob(KEY_BATCH_GLOB))


def list_export_batches(export_dir: Path) -> list[Path]:
    paths = sorted(export_dir.glob(EXPORT_BATCH_GLOB))
    if paths:
        return paths
    return sorted(export_dir.glob("*.csv"))


def pair_key_and_export_batches(
    batch_dir: Path,
    export_dir: Path,
) -> list[tuple[Path, Path | None]]:
    keys_by_num = {_batch_number(p): p for p in list_key_batches(batch_dir)}
    exports_by_num = {_batch_number(p): p for p in list_export_batches(export_dir)}
    nums = sorted(set(keys_by_num) | set(exports_by_num))
    return [(keys_by_num[n], exports_by_num.get(n)) for n in nums if n is not None]


def validate_export_batch(
    export_csv: Path,
    keys_csv: Path,
) -> dict[str, float | int | str]:
    """Coverage stats for one export file against its key batch."""
    if not export_csv.exists():
        return {"batch": export_csv.name, "error": "export_missing", "passed": False}
    if not keys_csv.exists():
        return {"batch": export_csv.name, "error": "keys_missing", "passed": False}
    stats = measure_geography_key_coverage(export_csv, keys_csv)
    n_keys = int(stats.get("n_keys", 0))
    thresholds = production_key_coverage_thresholds(n_keys) if n_keys >= 100 else None
    if thresholds is None:
        ok = float(stats.get("city_fill_rate", 0)) >= MIN_CITY_FILL
    else:
        ok, _ = evaluate_geography_acceptance(
            stats,
            thresholds=thresholds,
            label="batch",
            min_province_fill=MIN_PROVINCE_FILL,
            min_key_match_rate=KEY_COVERAGE_MIN_RATE,
        )
    return {**stats, "batch": export_csv.name, "keys_file": keys_csv.name, "passed": ok}


def validate_all_export_batches(
    batch_dir: Path,
    export_dir: Path,
) -> dict[str, object]:
    pairs = pair_key_and_export_batches(batch_dir, export_dir)
    results: list[dict] = []
    missing_exports = 0
    for keys_csv, export_csv in pairs:
        if export_csv is None:
            missing_exports += 1
            results.append(
                {
                    "batch": keys_csv.name,
                    "error": "export_missing",
                    "passed": False,
                    "keys_file": keys_csv.name,
                }
            )
            continue
        results.append(validate_export_batch(export_csv, keys_csv))
    passed = sum(1 for r in results if r.get("passed"))
    return {
        "n_key_batches": len(pairs),
        "n_export_batches": len(pairs) - missing_exports,
        "n_passed": passed,
        "all_passed": passed == len(pairs) and missing_exports == 0 and len(pairs) > 0,
        "batches": results,
    }


def concat_geography_batches(
    export_dir: Path,
    output: Path,
    *,
    pattern: str = EXPORT_BATCH_GLOB,
) -> int:
    """Concatenate batch exports with a unified header (streaming)."""
    files = sorted(export_dir.glob(pattern)) or sorted(export_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No export CSV files in {export_dir}")

    fieldnames: list[str] = []
    seen_cols: set[str] = set()
    for fp in files:
        with fp.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                continue
            for col in reader.fieldnames:
                if col not in seen_cols:
                    seen_cols.add(col)
                    fieldnames.append(col)

    rows_written = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for fp in files:
            with fp.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    writer.writerow(row)
                    rows_written += 1
    return rows_written


def _row_to_contract(row: dict[str, str], *, default_source: str, default_confidence: str) -> dict[str, str] | None:
    patent_id = _join_keys_from_row(row)
    if not patent_id:
        return None
    city = _pick_geo_field(row, ("applicant_city", "city", "申请人城市"))
    province = _pick_geo_field(row, ("applicant_province", "province", "申请人省份"))
    address = _pick_geo_field(row, ("applicant_address", "address", "申请人地址"))
    source = _non_empty_str(row.get("geo_source") or row.get("geography_source") or default_source)
    confidence = _non_empty_str(
        row.get("geo_match_confidence")
        or row.get("city_mapping_confidence")
        or default_confidence
    )
    notes = _non_empty_str(row.get("geo_notes") or row.get("notes"))
    return {
        "patent_id": patent_id,
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": address,
        "geo_source": source or default_source,
        "geo_match_confidence": confidence or default_confidence,
        "geo_notes": notes,
    }


def normalize_geography_batches(
    export_dir: Path,
    output_csv: Path,
    *,
    pattern: str = EXPORT_BATCH_GLOB,
    default_source: str = "",
    default_match_confidence: str = "exact_publication_number",
) -> dict[str, int | float]:
    """Normalize batch exports with SQLite dedupe (first location wins, low RAM)."""
    files = sorted(export_dir.glob(pattern)) or sorted(export_dir.glob("*.csv"))
    if not files:
        raise ValueError(f"No export files in {export_dir}")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        db_path = Path(tmp.name)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE geo (
                patent_id TEXT PRIMARY KEY,
                applicant_city TEXT,
                applicant_province TEXT,
                applicant_address TEXT,
                geo_source TEXT,
                geo_match_confidence TEXT,
                geo_notes TEXT
            )
            """
        )
        for fp in files:
            source_default = default_source or fp.stem
            for row in iter_geography_rows(fp):
                contract = _row_to_contract(
                    row,
                    default_source=source_default,
                    default_confidence=default_match_confidence,
                )
                if contract is None:
                    continue
                conn.execute(
                    """
                    INSERT OR IGNORE INTO geo
                    (patent_id, applicant_city, applicant_province, applicant_address,
                     geo_source, geo_match_confidence, geo_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        contract["patent_id"],
                        contract["applicant_city"],
                        contract["applicant_province"],
                        contract["applicant_address"],
                        contract["geo_source"],
                        contract["geo_match_confidence"],
                        contract["geo_notes"],
                    ),
                )
        conn.commit()

        n_city = n_province = 0
        n_rows = 0
        with output_csv.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=list(CONTRACT_COLUMNS))
            writer.writeheader()
            for row in conn.execute("SELECT * FROM geo ORDER BY patent_id"):
                n_rows += 1
                _pid, city, province, address, source, confidence, notes = row
                if _non_empty_str(city):
                    n_city += 1
                if _non_empty_str(province):
                    n_province += 1
                writer.writerow(
                    {
                        "patent_id": row[0],
                        "applicant_city": city or "",
                        "applicant_province": province or "",
                        "applicant_address": address or "",
                        "geo_source": source or "",
                        "geo_match_confidence": confidence or "",
                        "geo_notes": notes or "",
                    }
                )
    finally:
        conn.close()
        db_path.unlink(missing_ok=True)

    return {
        "rows": n_rows,
        "city_fill_rate": n_city / n_rows if n_rows else 0.0,
        "province_fill_rate": n_province / n_rows if n_rows else 0.0,
    }
