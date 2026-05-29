"""P14/P17 tiered geography coverage tables (frozen robustness layer)."""
from __future__ import annotations

import csv
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

DEFAULT_GEO = PROJECT_ROOT / "data/raw/patents/cnipa_patent_geography_2015_2024.csv"
DEFAULT_P14 = PROJECT_ROOT / "outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv"
DEFAULT_P17_TIERS = PROJECT_ROOT / "outputs/tables/table_P17_tiered_geography_tier_breakdown.csv"

P14_COLUMNS = [
    "geo_match_confidence",
    "rows",
    "share",
    "city_fill",
    "province_fill",
]

P17_TIER_COLUMNS = [
    "geo_match_confidence",
    "rows",
    "share",
    "city_fill",
    "province_fill",
    "n_keys_total",
    "overall_city_fill_rate",
]


def _non_empty(val: str) -> bool:
    return bool(str(val or "").strip().replace("nan", ""))


def compute_p14_rows(geo_path: Path) -> tuple[list[dict[str, str | float | int]], int]:
    buckets: dict[str, dict[str, int]] = {}
    n_total = 0

    with geo_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            n_total += 1
            conf = str(row.get("geo_match_confidence") or "").strip() or "unresolved"
            if conf not in buckets:
                buckets[conf] = {"rows": 0, "city": 0, "province": 0}
            buckets[conf]["rows"] += 1
            if _non_empty(str(row.get("applicant_city", ""))):
                buckets[conf]["city"] += 1
            if _non_empty(str(row.get("applicant_province", ""))):
                buckets[conf]["province"] += 1

    rows_out: list[dict[str, str | float | int]] = []
    for conf, counts in sorted(buckets.items(), key=lambda x: -x[1]["rows"]):
        n = counts["rows"]
        rows_out.append(
            {
                "geo_match_confidence": conf,
                "rows": n,
                "share": round(n / n_total, 6) if n_total else 0.0,
                "city_fill": round(counts["city"] / n, 6) if n else 0.0,
                "province_fill": round(counts["province"] / n, 6) if n else 0.0,
            }
        )
    return rows_out, n_total


def write_p14(
    geo_path: Path | None = None,
    output_path: Path | None = None,
) -> tuple[list[dict[str, str | float | int]], int]:
    geo_path = geo_path or DEFAULT_GEO
    output_path = output_path or DEFAULT_P14
    rows, n_total = compute_p14_rows(geo_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=P14_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows, n_total


def write_p17_tier_breakdown(
    p14_rows: list[dict[str, str | float | int]],
    *,
    n_keys_total: int,
    overall_city_fill_rate: float,
    output_path: Path | None = None,
) -> None:
    output_path = output_path or DEFAULT_P17_TIERS
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched: list[dict[str, str | float | int]] = []
    for row in p14_rows:
        enriched.append(
            {
                **row,
                "n_keys_total": n_keys_total,
                "overall_city_fill_rate": round(overall_city_fill_rate, 6),
            }
        )
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=P17_TIER_COLUMNS)
        writer.writeheader()
        writer.writerows(enriched)
