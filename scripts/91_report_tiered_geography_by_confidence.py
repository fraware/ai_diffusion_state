"""Write table P14 tiered geography coverage by geo_match_confidence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.tiered_coverage_tables import (  # noqa: E402
    DEFAULT_GEO,
    DEFAULT_P14,
    write_p14,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--geo", type=Path, default=DEFAULT_GEO)
    p.add_argument("--output", type=Path, default=DEFAULT_P14)
    args = p.parse_args()

    if not args.geo.exists():
        print(f"ERROR: missing {args.geo}", file=sys.stderr)
        return 1

    rows, n_keys = write_p14(args.geo, args.output)
    print({"n_keys": n_keys})
    for row in rows:
        print(row)
    print("wrote", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
