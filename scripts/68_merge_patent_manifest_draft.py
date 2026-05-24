"""Merge patent_source_manifest_draft.csv into patent_source_manifest.csv."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.patent_raw_sources import MANIFEST_COLUMNS, MANIFEST_PATH, RAW_PATENTS_DIR  # noqa: E402
from diffusion_state.validate_patent_source_manifest import validate_patent_source_manifest  # noqa: E402

DRAFT = RAW_PATENTS_DIR / "patent_source_manifest_draft.csv"


def merge_manifest(*, dry_run: bool = False, warn_only: bool = False) -> int:
    if not DRAFT.exists():
        print(f"ERROR: missing draft manifest {DRAFT}", file=sys.stderr)
        return 1
    draft = pd.read_csv(DRAFT)
    for col in MANIFEST_COLUMNS:
        if col not in draft.columns:
            draft[col] = ""
    draft = draft[MANIFEST_COLUMNS]
    if MANIFEST_PATH.exists():
        existing = pd.read_csv(MANIFEST_PATH)
        for col in MANIFEST_COLUMNS:
            if col not in existing.columns:
                existing[col] = ""
        existing = existing[MANIFEST_COLUMNS]
        keep = existing[~existing["source_file"].isin(draft["source_file"])]
        merged = pd.concat([keep, draft], ignore_index=True)
    else:
        merged = draft
    if dry_run:
        print(merged.to_string(index=False))
        return 0
    merged.to_csv(MANIFEST_PATH, index=False, encoding="utf-8-sig")
    print(f"Wrote merged manifest: {MANIFEST_PATH}")
    issues = validate_patent_source_manifest()
    if issues:
        print("Manifest validation issues (expected until FILL_ME fields and files exist):")
        for issue in issues:
            print(f"- {issue}")
        return 0 if warn_only else 2
    print("Manifest validation passed.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Merge patent manifest draft into patent_source_manifest.csv")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--warn-only",
        action="store_true",
        help="Return 0 after merge even if manifest validation fails (cloud copy-back path).",
    )
    args = p.parse_args()
    return merge_manifest(dry_run=args.dry_run, warn_only=args.warn_only)


if __name__ == "__main__":
    raise SystemExit(main())
