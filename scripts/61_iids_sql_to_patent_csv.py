"""Stream IIDS SQL dumps into an Atlas Phase-1 patent export CSV.

Requires locally downloaded SQL from scripts/59_download_iids_patent_sources.py.
Credentials stay in OPENXLAB_AK / OPENXLAB_SK only (script 59); this script reads SQL files.

Usage:
    python scripts/61_iids_sql_to_patent_csv.py
    python scripts/61_iids_sql_to_patent_csv.py --detail-sql path/to/base_patent_detail.sql
    python scripts/61_iids_sql_to_patent_csv.py --max-rows 5000

After conversion (and optional geography join via script 62):
    make atlas-patent-prep
    # complete patent_source_manifest.csv from draft
    make atlas-evidence-check
    make atlas-patents
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_patent_converter import (  # noqa: E402
    DEFAULT_OUTPUT,
    IIDS_SOURCES_DIR,
    IidsConvertConfig,
    convert_iids_sql_to_csv,
    find_iids_sql_paths,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Convert IIDS SQL dumps to Atlas Phase-1 CSV.")
    p.add_argument(
        "--detail-sql",
        type=Path,
        default=None,
        help="Path to base_patent_detail.sql (default: auto-discover under opendatalab_iids_sources/)",
    )
    p.add_argument(
        "--law-status-sql",
        type=Path,
        default=None,
        help="Optional path to base_patent_law_status.sql for grant_year enrichment",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT.relative_to(ROOT)})",
    )
    p.add_argument("--year-min", type=int, default=2015)
    p.add_argument("--year-max", type=int, default=2024)
    p.add_argument(
        "--all-jurisdictions",
        action="store_true",
        help="Do not restrict to CN publication numbers (default: CN only)",
    )
    p.add_argument(
        "--no-industrial-ai-filter",
        action="store_true",
        help="Disable taxonomy/IPC industrial-AI filter (not recommended for Atlas export)",
    )
    p.add_argument("--max-rows", type=int, default=None, help="Stop after N written rows (smoke tests)")
    return p


def main() -> int:
    args = _build_parser().parse_args()
    detail = args.detail_sql
    law = args.law_status_sql
    if detail is None or law is None:
        auto_detail, auto_law = find_iids_sql_paths(IIDS_SOURCES_DIR)
        detail = detail or auto_detail
        law = law if args.law_status_sql is not None else auto_law
    if detail is None or not detail.exists():
        print(
            "ERROR: base_patent_detail.sql not found.\n"
            "  1. Run: python scripts/59_download_iids_patent_sources.py --include-sql\n"
            "  2. Or pass --detail-sql with a local path (~136 GB download).\n"
            f"  Searched under: {IIDS_SOURCES_DIR}",
            file=sys.stderr,
        )
        return 1

    config = IidsConvertConfig(
        detail_sql=detail,
        law_status_sql=law if law and law.exists() else None,
        output_csv=args.output,
        year_min=args.year_min,
        year_max=args.year_max,
        jurisdiction_cn_only=not args.all_jurisdictions,
        require_industrial_ai=not args.no_industrial_ai_filter,
        max_rows=args.max_rows,
    )
    print(f"Detail SQL: {detail}")
    if config.law_status_sql:
        print(f"Law status SQL: {config.law_status_sql}")
    print(f"Output: {config.output_csv}")
    stats = convert_iids_sql_to_csv(config)
    print(
        "Done. "
        f"scanned={stats.scanned_rows} "
        f"year_filtered={stats.year_filtered} "
        f"jurisdiction_filtered={stats.jurisdiction_filtered} "
        f"ai_filtered={stats.ai_filtered} "
        f"written={stats.written_rows}"
    )
    if stats.written_rows == 0:
        print("WARNING: no rows written; check filters and SQL format.", file=sys.stderr)
        return 2
    print("\nNext:")
    print("  python scripts/62_join_iids_patent_geography.py   # if CNIPA geography supplement exists")
    print("  make atlas-patent-prep")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
