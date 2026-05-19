from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

PILOT_ZONE_COLUMNS = [
    "pilot_unit_id",
    "city",
    "province",
    "admin_level",
    "pilot_zone",
    "pilot_year",
    "created_date",
    "announced_date",
    "specialization_zh",
    "specialization_en",
    "source_url",
    "source_name",
    "date_quality",
    "notes",
]

MUNICIPALITIES = {"Beijing", "Shanghai", "Tianjin", "Chongqing"}

CSET_SOURCE = (
    "https://cset.georgetown.edu/publication/"
    "china-creates-national-new-generation-artificial-intelligence-"
    "innovation-and-development-pilot-zones/"
)


def _slugify_city(city: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", city.lower()).strip("_")
    return slug or "unknown"


def _infer_admin_level(city: str, province: str) -> str:
    if city == "Deqing":
        return "county"
    if city in MUNICIPALITIES and city == province:
        return "municipality"
    return "city"


def _infer_date_quality(created: str | float, announced: str | float) -> str:
    created_s = "" if pd.isna(created) else str(created).strip()
    announced_s = "" if pd.isna(announced) else str(announced).strip()
    if created_s and announced_s:
        return "exact_date"
    if created_s or announced_s:
        return "exact_year"
    return "inferred_year"


def _infer_source_name(source_url: str) -> str:
    if CSET_SOURCE in str(source_url):
        return "cset_most_initial_11"
    return "jjckb_2021_17_list"


def build_pilot_zones(seed_path: Path | None = None, out_path: Path | None = None) -> pd.DataFrame:
    """Build canonical pilot-zone treatment table from verified seed CSV."""
    seed_path = seed_path or PROJECT_ROOT / "data" / "seed" / "pilot_zones_seed.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"

    raw = pd.read_csv(seed_path)
    required_seed = {
        "location",
        "province_or_municipality",
        "pilot_year",
        "source_url",
    }
    missing = required_seed - set(raw.columns)
    if missing:
        raise ValueError(f"Missing columns in pilot seed: {sorted(missing)}")

    raw["pilot_year"] = pd.to_numeric(raw["pilot_year"], errors="raise").astype(int)

    city = raw["location"].str.replace(" County", "", regex=False).str.strip()
    province = raw["province_or_municipality"].astype(str).str.strip()
    created = raw.get("date_created", pd.Series([pd.NA] * len(raw)))
    announced = raw.get("date_announced", pd.Series([pd.NA] * len(raw)))
    specialization = raw.get("specialization_or_note", pd.Series([""] * len(raw))).fillna("")

    df = pd.DataFrame(
        {
            "pilot_unit_id": [_slugify_city(c) for c in city],
            "city": city,
            "province": province,
            "admin_level": [_infer_admin_level(c, p) for c, p in zip(city, province)],
            "pilot_zone": 1,
            "pilot_year": raw["pilot_year"],
            "created_date": created,
            "announced_date": announced,
            "specialization_zh": "",
            "specialization_en": specialization.astype(str),
            "source_url": raw["source_url"],
            "source_name": raw["source_url"].map(_infer_source_name),
            "date_quality": [
                _infer_date_quality(c, a) for c, a in zip(created, announced)
            ],
            "notes": "",
        }
    )

    # Deqing county mapping note
    deqing_mask = df["city"] == "Deqing"
    df.loc[deqing_mask, "notes"] = (
        "County-level pilot unit (Deqing County, Huzhou prefecture, Zhejiang). "
        "Mapped to admin_level=county; join to prefecture-level controls with care."
    )

    # Guangzhou/Wuhan: announced without created in seed
    for idx, row in df.iterrows():
        if row["city"] in {"Guangzhou", "Wuhan"} and pd.isna(row["created_date"]):
            df.at[idx, "notes"] = (
                "MOST-added zone; announcement date in jjckb source; "
                "creation date not in CSET first-11 table."
            )

    for idx, row in df.iterrows():
        if row["pilot_year"] == 2021 and row["date_quality"] == "inferred_year":
            existing = str(df.at[idx, "notes"])
            suffix = "Pilot year inferred from Dec 2021 national list; exact designation date unverified in seed."
            df.at[idx, "notes"] = f"{existing} {suffix}".strip()

    if df["pilot_unit_id"].duplicated().any():
        dupes = df.loc[df["pilot_unit_id"].duplicated(), "pilot_unit_id"].tolist()
        raise ValueError(f"Duplicate pilot_unit_id values: {dupes}")

    if df["city"].duplicated().any():
        dupes = df.loc[df["city"].duplicated(), "city"].tolist()
        raise ValueError(f"Duplicate normalized city names: {dupes}")

    df = df[PILOT_ZONE_COLUMNS].sort_values(["pilot_year", "city"]).reset_index(drop=True)
    write_csv(df, out_path)
    return df


if __name__ == "__main__":
    out = build_pilot_zones()
    print(f"Wrote {len(out)} pilot zones to data/processed/pilot_zones.csv")
