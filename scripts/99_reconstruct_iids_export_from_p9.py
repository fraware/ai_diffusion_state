"""Rebuild opendatalab IIDS export from P9 keys + tiered geography (post join-truncation recovery)."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_stream import load_geography_lookup_dict  # noqa: E402
from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS  # noqa: E402

DEFAULT_P9 = ROOT / "outputs/tables/table_P9_iids_patent_keys_for_geography.csv"
DEFAULT_GEO = ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024.csv"
DEFAULT_OUT = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
SOURCE_LABEL = "opendatalab_iids"
SOURCE_FILE = "reconstructed_from_table_P9_and_cnipa_patent_geography"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--p9", type=Path, default=DEFAULT_P9)
    p.add_argument("--geo", type=Path, default=DEFAULT_GEO)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--expected-rows", type=int, default=4_014_104)
    args = p.parse_args()

    if not args.p9.exists():
        print(f"ERROR: missing {args.p9}", file=sys.stderr)
        return 1
    if not args.geo.exists():
        print(f"ERROR: missing {args.geo}", file=sys.stderr)
        return 1

    print("Loading geography lookup...", flush=True)
    lookup = load_geography_lookup_dict(args.geo)
    print(f"lookup_patents={len(lookup)}", flush=True)

    tmp = args.output.with_suffix(args.output.suffix + ".reconstruct_tmp")
    n_rows = 0
    n_city = 0

    with args.p9.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in:
        reader = csv.DictReader(f_in)
        with tmp.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=PHASE1_COLUMNS)
            writer.writeheader()

            for row in reader:
                pid = str(row.get("patent_id") or row.get("publication_number") or "").strip()
                if not pid:
                    continue

                city, province, address = lookup.get(pid, ("", "", ""))
                if city:
                    n_city += 1

                writer.writerow(
                    {
                        "patent_id": pid,
                        "application_year": str(row.get("application_year") or "").strip(),
                        "publication_year": str(row.get("publication_year") or "").strip(),
                        "grant_year": "",
                        "applicant_name": str(row.get("applicant_name") or "").strip(),
                        "applicant_city": city,
                        "applicant_province": province,
                        "applicant_address": address,
                        "patent_title": str(row.get("patent_title") or "").strip(),
                        "abstract": "",
                        "claims_or_description": "",
                        "ipc_or_cpc": "",
                        "patent_type": "",
                        "source": SOURCE_LABEL,
                        "source_url_or_file": SOURCE_FILE,
                        "search_keyword": str(row.get("search_keyword") or "industrial_ai_taxonomy").strip(),
                    }
                )
                n_rows += 1
                if n_rows % 500_000 == 0:
                    print(
                        {
                            "rows": n_rows,
                            "city_fill": round(n_city / n_rows, 4),
                        },
                        flush=True,
                    )

    if n_rows < int(args.expected_rows * 0.99):
        print(
            f"ERROR: reconstructed {n_rows} rows, expected ~{args.expected_rows}",
            file=sys.stderr,
        )
        tmp.unlink(missing_ok=True)
        return 1

    tmp.replace(args.output)
    city_fill = round(n_city / max(n_rows, 1), 4)
    print(
        {
            "rows": n_rows,
            "city_fill": city_fill,
            "output": str(args.output),
            "bytes": args.output.stat().st_size,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
