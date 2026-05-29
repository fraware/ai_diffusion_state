"""Memory-efficient geography lookup load and IIDS join for multi-million-row exports."""
from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

from diffusion_state.iids_geo_join import (
    GEO_ADDRESS_COLUMNS,
    GEO_CITY_COLUMNS,
    GEO_PROVINCE_COLUMNS,
    _join_keys_from_row,
    _non_empty_str,
    summarize_geography_from_counts,
)
from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS

STREAMING_IIDS_BYTES = 50 * 1024 * 1024
GEO_LOOKUP_COLUMNS = ("applicant_city", "applicant_province", "applicant_address")


def load_patent_id_key_set(keys_csv: Path) -> set[str]:
    """Stream unique patent_id values from the filtered IIDS key list."""
    keys: set[str] = set()
    with keys_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            patent_id = _non_empty_str(row.get("patent_id", "")) or _non_empty_str(
                row.get("publication_number", "")
            )
            if patent_id:
                keys.add(patent_id)
    return keys


def should_stream_patent_csv(path: Path) -> bool:
    return path.exists() and path.stat().st_size >= STREAMING_IIDS_BYTES


def _filter_template_notes(row: dict[str, str]) -> bool:
    for col in ("geo_notes", "notes", "geo_match_confidence", "city_mapping_confidence"):
        val = row.get(col, "")
        if val and "TEMPLATE" in str(val).upper() and "DO NOT USE" in str(val).upper():
            return True
    return False


def iter_geography_rows(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Geography CSV has no header: {path}")
        for row in reader:
            if _filter_template_notes(row):
                continue
            yield row


def load_geography_lookup_dict(path: Path) -> dict[str, tuple[str, str, str]]:
    """Build patent_id -> (city, province, address); first non-empty location wins."""
    lookup: dict[str, tuple[str, str, str]] = {}
    for row in iter_geography_rows(path):
        patent_id = _join_keys_from_row(row)
        if not patent_id or patent_id in lookup:
            continue
        lookup[patent_id] = (
            _pick_geo_field(row, GEO_CITY_COLUMNS),
            _pick_geo_field(row, GEO_PROVINCE_COLUMNS),
            _pick_geo_field(row, GEO_ADDRESS_COLUMNS),
        )
    return lookup


def _pick_geo_field(row: dict[str, str], aliases: tuple[str, ...]) -> str:
    lower = {str(k).strip().lower(): k for k in row}
    for alias in aliases:
        key = lower.get(alias.lower())
        if key is None:
            continue
        val = _non_empty_str(row.get(key, ""))
        if val:
            return val
    return ""


def measure_geography_key_coverage(
    geography_csv: Path,
    keys_csv: Path,
) -> dict[str, float | int]:
    """Coverage rates on the filtered IIDS key population (publication-number join)."""
    lookup = load_geography_lookup_dict(geography_csv)
    n_keys = 0
    n_matched = 0
    n_city = 0
    n_province = 0
    cities: set[str] = set()

    with keys_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            patent_id = _non_empty_str(row.get("patent_id", "")) or _non_empty_str(
                row.get("publication_number", "")
            )
            if not patent_id:
                continue
            n_keys += 1
            geo = lookup.get(patent_id)
            if geo is None:
                continue
            n_matched += 1
            city, province, _address = geo
            if city:
                n_city += 1
                cities.add(city)
            if province:
                n_province += 1

    return summarize_geography_from_counts(
        n_keys=n_keys,
        n_matched=n_matched,
        n_city=n_city,
        n_province=n_province,
        n_unique_cities=len(cities),
    )


def join_patent_geography_streaming(
    iids_csv: Path,
    geo_csv: Path,
    output_csv: Path,
) -> dict[str, float | int]:
    lookup = load_geography_lookup_dict(geo_csv)
    n_rows = 0
    n_city = 0
    n_province = 0
    cities: set[str] = set()

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    # Never write in-place on Windows: opening the same path for write truncates the read handle.
    in_place = output_csv.resolve() == iids_csv.resolve()
    write_path = output_csv.with_suffix(output_csv.suffix + ".join_tmp") if in_place else output_csv

    with iids_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in:
        reader = csv.DictReader(f_in)
        if not reader.fieldnames:
            raise ValueError(f"IIDS CSV has no header: {iids_csv}")
        fieldnames = list(reader.fieldnames)
        for col in PHASE1_COLUMNS:
            if col not in fieldnames:
                fieldnames.append(col)

        with write_path.open("w", encoding="utf-8-sig", newline="") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in reader:
                n_rows += 1
                patent_id = _non_empty_str(row.get("patent_id", ""))
                geo = lookup.get(patent_id, ("", "", ""))
                city, province, address = geo
                for col, val in (
                    ("applicant_city", city),
                    ("applicant_province", province),
                    ("applicant_address", address),
                ):
                    if val and not _non_empty_str(row.get(col, "")):
                        row[col] = val
                city_val = _non_empty_str(row.get("applicant_city", ""))
                prov_val = _non_empty_str(row.get("applicant_province", ""))
                if city_val:
                    n_city += 1
                    cities.add(city_val)
                if prov_val:
                    n_province += 1
                out_row = {col: row.get(col, "") for col in fieldnames}
                writer.writerow(out_row)

    if in_place:
        write_path.replace(output_csv)

    return summarize_geography_from_counts(
        n_keys=n_rows,
        n_matched=n_rows,
        n_city=n_city,
        n_province=n_province,
        n_unique_cities=len(cities),
    )
