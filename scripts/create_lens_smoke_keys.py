"""Create 25-ID smoke key file from batch 001 for Lens API smoke test."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC = ROOT / "data/interim/iids_geo_key_batches/iids_geo_keys_batch_001.csv"
DEFAULT_OUT = ROOT / "data/interim/iids_geo_key_batches/iids_geo_keys_smoke_025.csv"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=DEFAULT_SRC)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--n", type=int, default=25)
    args = p.parse_args()

    if not args.source.exists():
        raise SystemExit(f"Missing source: {args.source}")

    rows: list[dict[str, str]] = []
    with args.source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or ["patent_id", "publication_number"]
        for row in reader:
            rows.append(row)
            if len(rows) >= args.n:
                break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print({"source": str(args.source), "output": str(args.output), "rows": len(rows)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
