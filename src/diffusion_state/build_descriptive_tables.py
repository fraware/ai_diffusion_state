from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"


def _read_processed(name: str) -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "data" / "processed" / name)


def build_table_1_dataset_summary() -> pd.DataFrame:
    pilots = _read_processed("pilot_zones.csv")
    clean = _read_processed("smart_factories_clean.csv")
    city_year = _read_processed("smart_factory_city_year.csv")
    prov_year = _read_processed("smart_factory_province_year.csv")

    rows = [
        {
            "dataset": "pilot_zones",
            "unit": "city/county",
            "observations": len(pilots),
            "years_covered": "2019-2021",
            "source": "data/processed/pilot_zones.csv",
        },
        {
            "dataset": "smart_factories_clean",
            "unit": "project",
            "observations": len(clean),
            "years_covered": "2024, 2025",
            "source": "data/processed/smart_factories_clean.csv",
        },
        {
            "dataset": "smart_factory_city_year",
            "unit": "city-year",
            "observations": len(city_year),
            "years_covered": "2024, 2025 (resolved cities)",
            "source": "data/processed/smart_factory_city_year.csv",
        },
        {
            "dataset": "smart_factory_province_year",
            "unit": "province-year",
            "observations": len(prov_year),
            "years_covered": "2024, 2025",
            "source": "data/processed/smart_factory_province_year.csv",
        },
        {
            "dataset": "smart_factories_city_unknown",
            "unit": "project",
            "observations": int((clean["city"] == "unknown").sum()),
            "years_covered": "2024, 2025",
            "source": "province-only location in MIIT tables",
        },
        {
            "dataset": "smart_factories_city_resolved",
            "unit": "project",
            "observations": int((clean["city"] != "unknown").sum()),
            "years_covered": "2024, 2025",
            "source": "parser + audited geo overrides",
        },
    ]
    return pd.DataFrame(rows)


def build_table_2_top_smart_factory_cities(top_n: int = 20) -> pd.DataFrame:
    cy = _read_processed("smart_factory_city_year.csv")
    pilots = set(_read_processed("pilot_zones.csv")["city"])
    totals = (
        cy.groupby(["city", "province"], as_index=False)["smart_factory_projects"]
        .sum()
        .rename(columns={"smart_factory_projects": "projects_total"})
    )
    by_year = cy.pivot_table(
        index=["city", "province"],
        columns="year",
        values="smart_factory_projects",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()
    by_year.columns = [
        "_".join(str(c) for c in col).strip("_") if isinstance(col, tuple) else str(col)
        for col in by_year.columns
    ]
    rename_map = {c: f"projects_{c}" for c in by_year.columns if str(c).isdigit()}
    by_year = by_year.rename(columns=rename_map)
    totals = totals.merge(by_year, on=["city", "province"], how="left")
    totals["pilot_zone_city"] = totals["city"].isin(pilots).astype(int)
    return totals.sort_values("projects_total", ascending=False).head(top_n)


def build_table_pilot_zone_overlap() -> pd.DataFrame:
    """Descriptive overlap: pilot-zone vs non-pilot-zone cities (resolved city only)."""
    cy = _read_processed("smart_factory_city_year.csv")
    pilots = _read_processed("pilot_zones.csv")[["city", "pilot_year"]]
    totals = (
        cy.groupby("city", as_index=False)["smart_factory_projects"]
        .sum()
        .rename(columns={"smart_factory_projects": "projects_2024_2025"})
    )
    totals = totals.merge(pilots, on="city", how="left")
    totals["pilot_zone_city"] = totals["pilot_year"].notna().astype(int)

    def _summarize(label: str, subset: pd.DataFrame) -> dict:
        return {
            "sample": label,
            "n_cities": len(subset),
            "total_projects_2024_2025": int(subset["projects_2024_2025"].sum()),
            "mean_projects_per_city": subset["projects_2024_2025"].mean(),
            "median_projects_per_city": subset["projects_2024_2025"].median(),
        }

    pilot = totals[totals["pilot_zone_city"] == 1]
    non_pilot = totals[totals["pilot_zone_city"] == 0]
    rows = [
        _summarize("pilot_zone_cities", pilot),
        _summarize("non_pilot_zone_cities", non_pilot),
        _summarize("all_resolved_cities", totals),
    ]
    diff = pd.DataFrame(rows)
    diff["mean_difference_pilot_minus_non"] = (
        diff.loc[diff["sample"] == "pilot_zone_cities", "mean_projects_per_city"].iloc[0]
        - diff.loc[diff["sample"] == "non_pilot_zone_cities", "mean_projects_per_city"].iloc[0]
    )
    return diff


def build_table_pilot_zone_province_overlap() -> pd.DataFrame:
    """Province-level overlap using all projects (includes unresolved city)."""
    clean = _read_processed("smart_factories_clean.csv")
    pilots = _read_processed("pilot_zones.csv")
    pilot_provinces = set(pilots["province"])
    clean = clean[clean["province"] != "unknown"]
    totals = (
        clean.groupby("province", as_index=False)
        .agg(smart_factory_projects=("project_id", "count"))
        .rename(columns={"smart_factory_projects": "projects_2024_2025"})
    )
    totals["pilot_zone_province"] = totals["province"].isin(pilot_provinces).astype(int)

    def _summarize(label: str, subset: pd.DataFrame) -> dict:
        return {
            "sample": label,
            "n_provinces": len(subset),
            "total_projects": int(subset["projects_2024_2025"].sum()),
            "mean_projects_per_province": subset["projects_2024_2025"].mean(),
        }

    pilot = totals[totals["pilot_zone_province"] == 1]
    non = totals[totals["pilot_zone_province"] == 0]
    rows = [
        _summarize("pilot_zone_provinces", pilot),
        _summarize("non_pilot_provinces", non),
        _summarize("all_provinces", totals),
    ]
    return pd.DataFrame(rows)


def build_all_descriptive_tables() -> dict[str, pd.DataFrame]:
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    tables = {
        "table_1_dataset_summary.csv": build_table_1_dataset_summary(),
        "table_2_top_smart_factory_cities.csv": build_table_2_top_smart_factory_cities(),
        "table_pilot_zone_overlap.csv": build_table_pilot_zone_overlap(),
        "table_pilot_zone_province_overlap.csv": build_table_pilot_zone_province_overlap(),
    }
    for name, df in tables.items():
        write_csv(df, OUTPUT_TABLES / name)
    return tables


if __name__ == "__main__":
    build_all_descriptive_tables()
