"""Normalize CNIPA/Lens geography exports to the Atlas contract CSV."""
from __future__ import annotations

import csv
from pathlib import Path

from diffusion_state.iids_geo_join import _join_keys_from_row
from diffusion_state.iids_geo_stream import iter_geography_rows, load_geography_lookup_dict

CONTRACT_COLUMNS = (
    "patent_id",
    "applicant_city",
    "applicant_province",
    "applicant_address",
    "geo_source",
    "geo_match_confidence",
    "geo_notes",
)


def normalize_geography_export(
    raw_csv: Path,
    output_csv: Path,
    *,
    geo_source: str = "",
    default_match_confidence: str = "exact_publication_number",
) -> dict[str, int | float]:
    """Read raw export, dedupe by patent_id, write contract CSV (streaming-safe)."""
    lookup = load_geography_lookup_dict(raw_csv)
    if not lookup:
        raise ValueError(f"No geography rows in {raw_csv}")

    meta: dict[str, tuple[str, str, str]] = {}
    for row in iter_geography_rows(raw_csv):
        patent_id = _join_keys_from_row(row)
        if not patent_id or patent_id in meta:
            continue
        source = (
            str(row.get("geo_source") or row.get("geography_source") or geo_source or raw_csv.stem)
            .strip()
        )
        confidence = str(
            row.get("geo_match_confidence")
            or row.get("city_mapping_confidence")
            or default_match_confidence
        ).strip()
        notes = str(row.get("geo_notes") or row.get("notes") or f"normalized from {raw_csv.name}").strip()
        meta[patent_id] = (source, confidence, notes)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    n_city = n_province = 0
    with output_csv.open("w", encoding="utf-8-sig", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=list(CONTRACT_COLUMNS))
        writer.writeheader()
        for patent_id, (city, province, address) in lookup.items():
            source, confidence, notes = meta.get(
                patent_id, (geo_source or raw_csv.stem, default_match_confidence, "")
            )
            if city:
                n_city += 1
            if province:
                n_province += 1
            writer.writerow(
                {
                    "patent_id": patent_id,
                    "applicant_city": city,
                    "applicant_province": province,
                    "applicant_address": address,
                    "geo_source": source,
                    "geo_match_confidence": confidence,
                    "geo_notes": notes,
                }
            )

    n = len(lookup)
    return {
        "rows": n,
        "city_fill_rate": n_city / n if n else 0.0,
        "province_fill_rate": n_province / n if n else 0.0,
    }
