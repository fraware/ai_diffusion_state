from __future__ import annotations

"""CI / pipeline-test city controls only — NOT for paper claims."""

from pathlib import Path
import shutil

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

STUB_NOTE = (
    "Synthetic city controls for pipeline/CI verification only. "
    "Do not cite in paper — replace with EPS/NBS via make city-controls."
)
STUB_SOURCE = "pipeline_ci_stub_not_for_paper"
RAW_STUB_NAME = "city_controls_ci_stub.csv"
PANEL_YEARS = list(range(2017, 2025))


def _tier_multiplier(city: str, pilot: bool) -> float:
    h = abs(hash(city)) % 1000
    base = 1.0 + (h % 50) / 100.0
    if pilot:
        base *= 1.35
    mega = {"Beijing", "Shanghai", "Shenzhen", "Guangzhou", "Hangzhou"}
    if city in mega:
        base *= 1.5
    return base


def _city_universe(panel_path: Path, pilot_path: Path) -> pd.DataFrame:
    if panel_path.exists():
        panel = pd.read_csv(panel_path)
        return panel[["city", "province"]].drop_duplicates()
    cy = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factory_city_year.csv")
    pilots = pd.read_csv(pilot_path)
    return pd.concat(
        [cy[["city", "province"]], pilots[["city", "province"]]],
        ignore_index=True,
    ).drop_duplicates("city")


def build_city_controls_ci_stub(
    panel_path: Path | None = None,
    pilot_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    pilot_path = pilot_path or PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"

    cities = _city_universe(panel_path, pilot_path)
    pilot_cities = set(pd.read_csv(pilot_path)["city"])
    rows = []
    for _, row in cities.iterrows():
        city = row["city"]
        if city == "unknown" or pd.isna(city):
            continue
        m = _tier_multiplier(city, city in pilot_cities)
        for year in PANEL_YEARS:
            yfac = 1.0 + 0.04 * (year - 2017)
            rows.append(
                {
                    "city": city,
                    "province": row["province"],
                    "year": year,
                    "gdp": round(800.0 * m * yfac, 2),
                    "gdp_per_capita": round(85000 * m, 0),
                    "secondary_value_added": round(320.0 * m * yfac, 2),
                    "industrial_output": round(280.0 * m * yfac, 2),
                    "population": round(6.5 * m * (1 + 0.01 * (year - 2017)), 3),
                    "employment": round(3.2 * m, 3),
                    "average_wage": round(95000 * m, 0),
                    "fdi": round(12.0 * m * yfac, 2),
                    "fixed_asset_investment": round(180.0 * m * yfac, 2),
                    "education_proxy": round(0.15 * m, 4),
                    "telecom_or_internet_proxy": round(0.72 * m, 4),
                    "foreign_trade": round(220.0 * m * yfac, 2),
                    "source_name": STUB_SOURCE,
                    "source_file": RAW_STUB_NAME,
                }
            )

    out = pd.DataFrame(rows)
    write_csv(out, out_path)
    miss = pd.DataFrame(
        [{"variable": "all", "share_missing": 0.0, "n_missing": 0, "n_obs": len(out)}]
    )
    write_csv(miss, PROJECT_ROOT / "data" / "processed" / "city_controls_missingness.csv")
    return out


def install_ci_stub_to_raw() -> Path:
    """Copy processed stub into data/raw/city_controls/ for build_city_controls_year()."""
    raw_dir = PROJECT_ROOT / "data" / "raw" / "city_controls"
    raw_dir.mkdir(parents=True, exist_ok=True)
    dest = raw_dir / RAW_STUB_NAME
    stub = build_city_controls_ci_stub()
    write_csv(stub, dest)
    return dest
