from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.utils import PROJECT_ROOT, read_yaml, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"

PRIMARY_CONFIDENCE = {"high", "medium"}


def build_export_bridge_audit() -> pd.DataFrame:
    bridge = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "hs_to_smart_factory_sector_bridge.csv")
    audit = bridge.copy()
    audit["analysis_tier"] = audit["mapping_confidence"].apply(
        lambda c: "primary" if c in PRIMARY_CONFIDENCE else "appendix_only"
    )
    write_csv(audit, OUTPUT_TABLES / "table_10_export_bridge_audit.csv")
    return audit


def _add_sector_growth_cols(sector: pd.DataFrame) -> pd.DataFrame:
    sector = sector.sort_values(["sector_group", "year"])
    sector["china_world_market_share_growth"] = sector.groupby("sector_group")[
        "china_world_market_share"
    ].pct_change()
    sector["hs6_count_growth"] = sector.groupby("sector_group")["hs6_count"].pct_change()
    return sector


def _sector_group_map() -> dict[str, str]:
    cfg = read_yaml(PROJECT_ROOT / "configs" / "export_sector_groups.yml")
    mapping: dict[str, str] = {}
    for group, spec in cfg.get("sector_groups", {}).items():
        for label in spec.get("labels", []):
            mapping[label] = group
    return mapping


def build_export_sector_descriptives() -> pd.DataFrame:
    sector = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv")
    bridge = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "hs_to_smart_factory_sector_bridge.csv")
    label_map = bridge.drop_duplicates("smart_factory_industry_label").set_index(
        "smart_factory_industry_label"
    )["mapping_confidence"]
    group_map = _sector_group_map()

    sector = sector[sector["mapping_confidence_summary"].isin(PRIMARY_CONFIDENCE)].copy()
    sector["sector_group"] = sector["sector_label"].map(group_map).fillna("other")
    sector = _add_sector_growth_cols(sector)

    desc = (
        sector.groupby(["sector_group", "year"], as_index=False)
        .agg(
            export_value_usd=("export_value_usd", "sum"),
            export_value_growth=("export_value_growth", "mean"),
            unit_value_growth=("unit_value_growth", "mean"),
            china_world_market_share_growth=("china_world_market_share_growth", "mean"),
            hs6_count_growth=("hs6_count_growth", "mean"),
            n_sector_codes=("sector_code", "nunique"),
        )
    )
    desc["note"] = "hs6_count_growth is HS6-product-count growth, not destination count."
    write_csv(desc, OUTPUT_TABLES / "table_11_export_sector_descriptives.csv")
    return desc


def build_export_models_revised() -> pd.DataFrame:
    sector = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv")
    clean = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv")
    group_map = _sector_group_map()

    prov_ind = (
        clean[clean["province"] != "unknown"]
        .assign(sector_group=lambda d: d["industry_label"].map(group_map).fillna("other"))
        .groupby(["province", "sector_group", "list_year"], as_index=False)
        .agg(smart_factory_projects=("project_id", "count"))
        .rename(columns={"list_year": "year"})
    )
    prov_ind["prov_year_total"] = prov_ind.groupby(["province", "year"])["smart_factory_projects"].transform(
        "sum"
    )
    prov_ind["sf_share"] = np.where(
        prov_ind["prov_year_total"] > 0,
        prov_ind["smart_factory_projects"] / prov_ind["prov_year_total"],
        0.0,
    )
    exposure = (
        prov_ind.groupby(["sector_group", "year"], as_index=False)["sf_share"]
        .mean()
        .rename(columns={"sf_share": "mean_province_sf_share"})
    )

    sector = sector[sector["mapping_confidence_summary"].isin(PRIMARY_CONFIDENCE)].copy()
    sector["sector_group"] = sector["sector_label"].map(group_map).fillna("other")
    sector = _add_sector_growth_cols(sector)
    sector_g = (
        sector.groupby(["sector_group", "year"], as_index=False)
        .agg(
            export_value_growth=("export_value_growth", "mean"),
            unit_value_growth=("unit_value_growth", "mean"),
            china_world_market_share_growth=("china_world_market_share_growth", "mean"),
            hs6_count_growth=("hs6_count_growth", "mean"),
        )
    )
    merged = sector_g.merge(exposure, on=["sector_group", "year"], how="inner").dropna(
        subset=["export_value_growth", "mean_province_sf_share"]
    )

    rows = []
    for outcome in [
        "export_value_growth",
        "unit_value_growth",
        "china_world_market_share_growth",
        "hs6_count_growth",
    ]:
        formula = f"{outcome} ~ mean_province_sf_share + C(year)"
        if len(merged) < 8:
            rows.append(
                {
                    "term": "skipped",
                    "coef": f"insufficient sector-group-years (n={len(merged)})",
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "n_obs": len(merged),
                    "r_squared": np.nan,
                    "model": f"revised_{outcome}",
                    "formula": formula,
                    "note": "Descriptive; high/medium-confidence bridge only.",
                }
            )
            continue
        fit = smf.ols(formula, data=merged).fit(cov_type="HC1")
        for term in fit.params.index:
            rows.append(
                {
                    "term": term,
                    "coef": fit.params[term],
                    "std_err": fit.bse[term],
                    "p_value": fit.pvalues[term],
                    "n_obs": int(fit.nobs),
                    "r_squared": fit.rsquared,
                    "model": f"revised_{outcome}",
                    "formula": formula,
                    "note": "Descriptive; high/medium-confidence bridge only.",
                }
            )

    out = pd.DataFrame(rows)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_12_export_models_revised.csv")
    return out


def build_export_sector_trends_figure() -> Path | None:
    desc_path = OUTPUT_TABLES / "table_11_export_sector_descriptives.csv"
    if not desc_path.exists():
        return None
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    desc = pd.read_csv(desc_path)
    groups = desc["sector_group"].unique()[:9]
    fig, ax = plt.subplots(figsize=(10, 5))
    for g in groups:
        sub = desc[desc["sector_group"] == g]
        ax.plot(sub["year"], sub["export_value_growth"], marker="o", label=g)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title("Sector-group export value growth (BACI, descriptive)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean export value growth")
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_FIGURES / "fig_export_sector_trends.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def build_export_relevance_by_sector() -> pd.DataFrame:
    """Descriptive strategic relevance: smart-factory concentration vs export basket."""
    clean = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv")
    sector = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv")
    bridge = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "hs_to_smart_factory_sector_bridge.csv")
    group_map = _sector_group_map()

    sf = (
        clean.assign(sector_group=lambda d: d["industry_label"].map(group_map).fillna("other"))
        .groupby("sector_group", as_index=False)
        .agg(smart_factory_projects=("project_id", "count"))
    )
    total_sf = int(sf["smart_factory_projects"].sum())
    sf["share_of_smart_factory_projects"] = sf["smart_factory_projects"] / total_sf if total_sf else 0.0

    sector = sector[sector["mapping_confidence_summary"].isin(PRIMARY_CONFIDENCE)].copy()
    sector["sector_group"] = sector["sector_label"].map(group_map).fillna("other")
    s2024 = sector[sector["year"] == 2024]
    export_2024 = (
        s2024.groupby("sector_group", as_index=False)
        .agg(export_value_2024=("export_value_usd", "sum"))
    )
    total_export = float(export_2024["export_value_2024"].sum())
    export_2024["share_of_china_exports_2024"] = (
        export_2024["export_value_2024"] / total_export if total_export else 0.0
    )

    def _cumulative_growth(g: pd.DataFrame) -> pd.Series:
        e17 = g.loc[g["year"] == 2017, "export_value_usd"]
        e24 = g.loc[g["year"] == 2024, "export_value_usd"]
        u17 = g.loc[g["year"] == 2017, "unit_value_index"]
        u24 = g.loc[g["year"] == 2024, "unit_value_index"]
        export_value_2017 = float(e17.sum()) if len(e17) else np.nan
        export_value_2024 = float(e24.sum()) if len(e24) else np.nan
        unit_value_index_2017 = float(u17.mean()) if len(u17) and u17.notna().any() else np.nan
        unit_value_index_2024 = float(u24.mean()) if len(u24) and u24.notna().any() else np.nan
        log_export = (
            np.log(export_value_2024) - np.log(export_value_2017)
            if export_value_2017 > 0 and export_value_2024 > 0
            else np.nan
        )
        log_unit = (
            np.log(unit_value_index_2024) - np.log(unit_value_index_2017)
            if unit_value_index_2017 > 0 and unit_value_index_2024 > 0
            else np.nan
        )
        return pd.Series(
            {
                "export_value_2017": export_value_2017,
                "export_value_2024": export_value_2024,
                "log_export_growth_2017_2024": log_export,
                "unit_value_index_2017": unit_value_index_2017,
                "unit_value_index_2024": unit_value_index_2024,
                "log_unit_value_growth_2017_2024": log_unit,
                "growth_method": "log_level_2017_2024",
            }
        )

    growth = sector.groupby("sector_group").apply(_cumulative_growth, include_groups=False).reset_index()

    conf = (
        bridge.assign(sector_group=lambda d: d["smart_factory_industry_label"].map(group_map).fillna("other"))
        .groupby("sector_group")["mapping_confidence"]
        .agg(lambda s: "high" if (s == "high").any() else ("medium" if (s == "medium").any() else s.iloc[0]))
        .reset_index()
        .rename(columns={"mapping_confidence": "mapping_confidence"})
    )

    out = sf.merge(export_2024, on="sector_group", how="left").merge(growth, on="sector_group", how="left")
    out = out.merge(conf, on="sector_group", how="left")
    out["note"] = "Descriptive strategic relevance; not a causal export effect."
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_15_export_relevance_by_sector.csv")
    return out


def build_all_export_revised() -> None:
    if not (PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv").exists():
        return
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    build_export_bridge_audit()
    build_export_sector_descriptives()
    build_export_models_revised()
    build_export_relevance_by_sector()
    build_export_sector_trends_figure()
