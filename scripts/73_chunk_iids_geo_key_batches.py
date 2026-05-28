"""Split IIDS geography key list into batch CSVs for CNIPA/Lens export."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_paths import FILTERED_PATENT_IDS_FOR_GEO_OUTPUT  # noqa: E402

DEFAULT_OUTDIR = ROOT / "data" / "interim" / "iids_geo_key_batches"
DEFAULT_BATCH_SIZE = 250_000


def chunk_geo_keys(
    src: Path,
    outdir: Path,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    batch_idx = 1
    rows_written = 0
    f_out = None
    writer = None

    with src.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if f_out is None or rows_written >= batch_size:
                if f_out:
                    f_out.close()
                out = outdir / f"iids_geo_keys_batch_{batch_idx:03d}.csv"
                f_out = out.open("w", encoding="utf-8-sig", newline="")
                writer = csv.DictWriter(f_out, fieldnames=["patent_id", "publication_number"])
                writer.writeheader()
                print("writing", out)
                written.append(out)
                batch_idx += 1
                rows_written = 0

            writer.writerow(
                {
                    "patent_id": row["patent_id"],
                    "publication_number": row["publication_number"],
                }
            )
            rows_written += 1

    if f_out:
        f_out.close()
    return written


def main() -> int:
    p = argparse.ArgumentParser(description="Chunk IIDS geography keys for database export.")
    p.add_argument("--src", type=Path, default=FILTERED_PATENT_IDS_FOR_GEO_OUTPUT)
    p.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    p.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    args = p.parse_args()
    if not args.src.exists():
        print(f"ERROR: key file not found: {args.src}", file=sys.stderr)
        return 1
    paths = chunk_geo_keys(args.src, args.outdir, batch_size=args.batch_size)
    print(f"done: {len(paths)} batch file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
