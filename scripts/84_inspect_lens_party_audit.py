"""Inspect Lens party-field audit CSV (Step 1 diagnostic)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "outputs/debug/lens_smoke_025_party_field_audit.csv"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--path", type=Path, default=DEFAULT_AUDIT)
    args = p.parse_args()

    if not args.path.exists():
        print(f"ERROR: missing {args.path}", file=sys.stderr)
        return 1

    df = pd.read_csv(args.path, low_memory=False, encoding="utf-8-sig")
    print(df.columns.tolist())
    for col in df.columns:
        if "address" in col.lower() or "residence" in col.lower():
            fill = (
                df[col]
                .astype(str)
                .str.strip()
                .replace({"nan": "", "None": ""})
                .ne("")
                .mean()
            )
            print(col, round(fill, 4))
    print(df.head(25).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
