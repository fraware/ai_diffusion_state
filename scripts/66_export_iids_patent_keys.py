"""Export publication numbers from IIDS CSV for targeted CNIPA/Lens geography acquisition."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_patent_keys import export_patent_keys_for_geography  # noqa: E402
from diffusion_state.iids_paths import (  # noqa: E402
    DEFAULT_IIDS_OUTPUT,
    PATENT_KEYS_FOR_GEO_OUTPUT,
    resolve_iids_output_csv,
)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Export patent_id/publication_number keys for geography-only CNIPA/Lens export."
    )
    p.add_argument("--iids-csv", type=Path, default=None, help="Filtered IIDS patent CSV")
    p.add_argument("--output", type=Path, default=PATENT_KEYS_FOR_GEO_OUTPUT)
    p.add_argument(
        "--production",
        action="store_true",
        help=f"Read evidence CSV ({DEFAULT_IIDS_OUTPUT.name})",
    )
    args = p.parse_args()

    iids_csv = args.iids_csv or resolve_iids_output_csv(production=args.production or args.iids_csv is None)
    if not iids_csv.exists():
        print(
            f"ERROR: IIDS CSV not found: {iids_csv}\n"
            "Run script 61 first, or pass --iids-csv.",
            file=sys.stderr,
        )
        return 1

    try:
        stats = export_patent_keys_for_geography(iids_csv, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Input rows: {stats.input_rows}")
    print(f"Unique patent IDs: {stats.unique_patent_ids}")
    print(f"Wrote: {stats.output_path}")
    print("\nUse this file to request geography-only export from CNIPA/Lens/CNKI/CSMAR.")
    print("Then: make atlas-iids-geo-build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
