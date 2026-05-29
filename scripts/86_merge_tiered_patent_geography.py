"""Streaming tiered merge: exact external > manual top applicant > inference tiers."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_normalize import CONTRACT_COLUMNS  # noqa: E402
from diffusion_state.tiered_geography_resolve import (  # noqa: E402
    UNRESOLVED_LABEL,
    resolve_tiered_geography,
)

DEFAULT_TOP_MAP = ROOT / "data/seed/top_applicant_city_map.csv"
DEFAULT_EXTERNAL_GLOB = "cnipa_patent_geography_2015_2024_external*.csv"
DEFAULT_OUTPUT = ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024.csv"
DEFAULT_IIDS = ROOT / "data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
DEFAULT_P14 = ROOT / "outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv"


def _non_empty(val: str) -> bool:
    return bool(str(val or "").strip())


def _load_external(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None or not path.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            pid = str(row.get("patent_id") or row.get("publication_number") or "").strip()
            if pid:
                out[pid] = row
    return out


def _load_top_applicant_map(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            name = str(row.get("applicant_name") or "").strip()
            city = str(row.get("applicant_city") or "").strip()
            if name and city:
                out[name] = row
    return out


def _write_p14(tier_buckets: dict[str, dict[str, int]], output: Path, n_total: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "geo_match_confidence",
                "rows",
                "share",
                "city_fill",
                "province_fill",
            ],
        )
        writer.writeheader()
        for conf, counts in sorted(tier_buckets.items(), key=lambda x: -x[1]["rows"]):
            n = counts["rows"]
            writer.writerow(
                {
                    "geo_match_confidence": conf,
                    "rows": n,
                    "share": round(n / n_total, 6) if n_total else 0.0,
                    "city_fill": round(counts["city"] / n, 6) if n else 0.0,
                    "province_fill": round(counts["province"] / n, 6) if n else 0.0,
                }
            )


def merge_streaming(
    *,
    iids_csv: Path,
    top_map: dict[str, dict[str, str]],
    external: dict[str, dict[str, str]],
    output_csv: Path,
    p14_output: Path,
) -> dict[str, object]:
    tier_buckets: dict[str, dict[str, int]] = {}
    n_rows = 0
    n_city = 0

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with iids_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in:
        reader = csv.DictReader(f_in)
        with output_csv.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=list(CONTRACT_COLUMNS))
            writer.writeheader()

            for row in reader:
                pid = str(row.get("patent_id") or "").strip()
                if not pid:
                    continue

                merged, tier = resolve_tiered_geography(
                    patent_id=pid,
                    applicant_name=str(row.get("applicant_name") or ""),
                    external=external,
                    top_map=top_map,
                )
                writer.writerow({"patent_id": pid, **merged})

                n_rows += 1
                if _non_empty(merged.get("applicant_city", "")):
                    n_city += 1

                if tier not in tier_buckets:
                    tier_buckets[tier] = {"rows": 0, "city": 0, "province": 0}
                tier_buckets[tier]["rows"] += 1
                if _non_empty(merged.get("applicant_city", "")):
                    tier_buckets[tier]["city"] += 1
                if _non_empty(merged.get("applicant_province", "")):
                    tier_buckets[tier]["province"] += 1

                if n_rows % 500_000 == 0:
                    print(
                        {"rows": n_rows, "city_fill": round(n_city / n_rows, 4)},
                        flush=True,
                    )

    _write_p14(tier_buckets, p14_output, n_rows)
    tier_counts = {k: v["rows"] for k, v in tier_buckets.items()}
    return {
        "rows": n_rows,
        "city_fill": round(n_city / max(n_rows, 1), 4),
        "tier_counts": tier_counts,
        "output": str(output_csv),
        "p14": str(p14_output),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--iids", type=Path, default=DEFAULT_IIDS)
    p.add_argument("--top-map", type=Path, default=DEFAULT_TOP_MAP)
    p.add_argument("--external", type=Path, default=None)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--p14-output", type=Path, default=DEFAULT_P14)
    args = p.parse_args()

    if not args.iids.exists():
        print(f"ERROR: missing {args.iids}", file=sys.stderr)
        return 1

    external_path = args.external
    if external_path is None:
        candidates = sorted((ROOT / "data/raw/patents").glob(DEFAULT_EXTERNAL_GLOB))
        external_path = candidates[0] if candidates else None

    external = _load_external(external_path)
    top_map = _load_top_applicant_map(args.top_map)

    stats = merge_streaming(
        iids_csv=args.iids,
        top_map=top_map,
        external=external,
        output_csv=args.output,
        p14_output=args.p14_output,
    )
    stats["external_rows"] = len(external)
    stats["top_map_applicants"] = len(top_map)
    print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
