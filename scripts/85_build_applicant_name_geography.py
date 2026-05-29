"""Build high-precision applicant-name city-token geography from IIDS export."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.china_city_gazetteer import geography_from_applicant_name  # noqa: E402
from diffusion_state.iids_geography_normalize import CONTRACT_COLUMNS  # noqa: E402

DEFAULT_INPUT = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_OUTPUT = (
    ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024_applicant_name_inferred.csv"
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--limit", type=int, default=0, help="Max rows (0 = all)")
    args = p.parse_args()

    if not args.input.exists():
        print(f"ERROR: missing {args.input}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)

    n_rows = 0
    n_city = 0
    n_province = 0

    with args.input.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in:
        reader = csv.DictReader(f_in)
        with args.output.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=list(CONTRACT_COLUMNS))
            writer.writeheader()

            for row in reader:
                patent_id = str(row.get("patent_id") or "").strip()
                if not patent_id:
                    continue

                geo = geography_from_applicant_name(str(row.get("applicant_name") or ""))
                writer.writerow({"patent_id": patent_id, **geo})

                n_rows += 1
                if geo["applicant_city"]:
                    n_city += 1
                if geo["applicant_province"]:
                    n_province += 1

                if n_rows % 500_000 == 0:
                    print(
                        {
                            "rows": n_rows,
                            "city_fill": round(n_city / n_rows, 4),
                            "province_fill": round(n_province / n_rows, 4),
                        },
                        flush=True,
                    )

                if args.limit and n_rows >= args.limit:
                    break

    print(
        {
            "rows": n_rows,
            "city_rows": n_city,
            "province_rows": n_province,
            "city_fill": round(n_city / max(n_rows, 1), 4),
            "province_fill": round(n_province / max(n_rows, 1), 4),
            "output": str(args.output),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
