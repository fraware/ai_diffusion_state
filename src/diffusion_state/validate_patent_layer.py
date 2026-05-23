from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.patent_taxonomy import CATEGORY_COLUMNS
from diffusion_state.utils import PROJECT_ROOT

YEAR_MIN = 2015
YEAR_MAX = 2024
MIN_CITIES = 50
MIN_INDUSTRIES = 10
MIN_CATEGORIES = 5
MIN_CITY_FILL_RATE = 0.80


def validate_patent_layer(
    long_path: Path | None = None,
    panel_path: Path | None = None,
) -> tuple[bool, list[str]]:
    long_path = long_path or PROJECT_ROOT / "data" / "interim" / "industrial_ai_patents_long.csv"
    panel_path = panel_path or (
        PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
    )
    issues: list[str] = []

    if not long_path.exists():
        issues.append(f"MISSING interim long file: {long_path}")
        return False, issues

    long_df = pd.read_csv(long_path)
    micro = long_df[long_df["source"] != "cset_1790"] if "source" in long_df.columns else long_df

    if micro.empty:
        issues.append(
            "BLOCKER: no CNIPA/normalized patent microdata in data/raw/patents/. "
            "Place cnipa_*.csv or patents_normalized*.csv with applicant city and text fields."
        )
        return False, issues

    if "is_industrial_ai" in micro.columns:
        non_classified = micro[
            (micro["is_industrial_ai"] == 0) & (micro["is_excluded_non_industrial"] == 0)
        ]
        if len(non_classified) == len(micro):
            issues.append("All microdata patents lack industrial AI category assignment.")

    years = pd.to_numeric(micro.get("application_year"), errors="coerce").dropna()
    if len(years):
        if years.min() < YEAR_MIN or years.max() > YEAR_MAX:
            issues.append(f"Years outside target range {YEAR_MIN}-{YEAR_MAX}: {years.min()}-{years.max()}")

    city_rate = micro["city"].astype(str).str.len().gt(0).mean() if "city" in micro.columns else 0
    if city_rate < MIN_CITY_FILL_RATE:
        issues.append(f"City fill rate {city_rate:.1%} below {MIN_CITY_FILL_RATE:.0%}")

    if not panel_path.exists():
        issues.append(f"MISSING processed panel: {panel_path}")
        return False, issues

    panel = pd.read_csv(panel_path)
    if panel.empty:
        issues.append("Processed city-industry-year panel is empty.")
        return False, issues

    n_cities = panel["city"].nunique()
    n_industries = panel["industry_code"].nunique()
    cats_populated = sum(
        1 for c in CATEGORY_COLUMNS if f"{c}_patents" in panel.columns and panel[f"{c}_patents"].sum() > 0
    )

    if n_cities < MIN_CITIES:
        issues.append(f"Only {n_cities} cities in panel (minimum {MIN_CITIES}).")
    if n_industries < MIN_INDUSTRIES:
        issues.append(f"Only {n_industries} industries in panel (minimum {MIN_INDUSTRIES}).")
    if cats_populated < MIN_CATEGORIES:
        issues.append(f"Only {cats_populated} taxonomy categories populated (minimum {MIN_CATEGORIES}).")

    dupes = panel.duplicated(subset=["city", "industry_code", "year"]).sum()
    if dupes:
        issues.append(f"Duplicate city-industry-year rows: {dupes}")

    raw_only = panel[panel["industrial_ai_patents"] > 0]
    if raw_only.empty:
        issues.append("No industrial_ai_patents counts in main panel.")

    ok = len(issues) == 0
    return ok, issues
