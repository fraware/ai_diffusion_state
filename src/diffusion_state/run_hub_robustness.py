from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.model_utils import control_terms, fit_ols_table
from diffusion_state.panel_controls import add_derived_controls, adoption_sample_with_controls, controls_available
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"

HUB_CITIES = {"Beijing", "Shanghai", "Shenzhen", "Hangzhou", "Guangzhou"}
DIRECT_ADMIN = {"Beijing", "Shanghai", "Tianjin", "Chongqing"}

INTERPRETATIONS: dict[str, str] = {
    "full_sample": "baseline association (all resolved cities)",
    "drop_beijing_shanghai_shenzhen_hangzhou": "association weakens after dropping four mega-hubs",
    "drop_beijing_shanghai_shenzhen_hangzhou_guangzhou": "association weakens after dropping five mega-hubs",
    "drop_direct_admin_municipalities": "association weakens substantially when direct-admin municipalities excluded",
    "drop_top_5_smart_factory_cities": "association weakens when top adoption cities excluded",
    "drop_top_10_gdp_cities": "association under top-GDP-city exclusion (requires GDP controls)",
}


def _top_smart_factory_cities(n: int) -> set[str]:
    cy = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factory_city_year.csv")
    totals = cy.groupby("city")["smart_factory_projects"].sum().sort_values(ascending=False)
    return set(totals.head(n).index)


def _top_gdp_cities(n: int, panel: pd.DataFrame) -> set[str]:
    pre = panel[panel["year"] == 2018].dropna(subset=["gdp"])
    if pre.empty:
        pre = panel.dropna(subset=["gdp"]).sort_values("year").groupby("city").tail(1)
    ranked = pre.groupby("city")["gdp"].max().sort_values(ascending=False)
    return set(ranked.head(n).index)


def _apply_exclusion(sample: pd.DataFrame, rule: str) -> pd.DataFrame:
    if rule == "full_sample":
        return sample
    if rule == "drop_beijing_shanghai_shenzhen_hangzhou":
        return sample[~sample["city"].isin(HUB_CITIES - {"Guangzhou"})]
    if rule == "drop_beijing_shanghai_shenzhen_hangzhou_guangzhou":
        return sample[~sample["city"].isin(HUB_CITIES)]
    if rule == "drop_direct_admin_municipalities":
        return sample[~sample["city"].isin(DIRECT_ADMIN)]
    if rule == "drop_top_5_smart_factory_cities":
        return sample[~sample["city"].isin(_top_smart_factory_cities(5))]
    if rule == "drop_top_10_gdp_cities":
        return sample[~sample["city"].isin(_top_gdp_cities(10, sample))]
    raise ValueError(f"Unknown exclusion rule: {rule}")


EXCLUSION_RULES = [
    "full_sample",
    "drop_beijing_shanghai_shenzhen_hangzhou",
    "drop_beijing_shanghai_shenzhen_hangzhou_guangzhou",
    "drop_direct_admin_municipalities",
    "drop_top_5_smart_factory_cities",
    "drop_top_10_gdp_cities",
]


def _run_spec(
    panel: pd.DataFrame,
    *,
    spec: str,
    use_controls: bool,
) -> pd.DataFrame:
    has_controls = controls_available(panel)
    ctrl = control_terms() if has_controls and use_controls else ""

    if use_controls:
        if not has_controls:
            return pd.DataFrame()
        base = adoption_sample_with_controls(panel)
        model_name = "controlled_count"
        formula = f"smart_factory_projects ~ pilot_zone + C(year) + {ctrl}"
    else:
        base = panel[panel["year"].isin((2024, 2025))].dropna(
            subset=["city", "smart_factory_projects", "pilot_zone"]
        )
        model_name = "baseline_count"
        formula = "smart_factory_projects ~ pilot_zone + C(year)"

    rows: list[dict] = []
    full_coef: float | None = None
    full_projects = 0

    for rule in EXCLUSION_RULES:
        if rule == "drop_top_10_gdp_cities" and not panel["gdp"].notna().any():
            rows.append(
                {
                    "exclusion_rule": rule,
                    "spec": spec,
                    "n_cities": 0,
                    "n_projects": 0,
                    "model": "skipped",
                    "term": "skipped",
                    "coef": "gdp controls unavailable for top-10 GDP exclusion",
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "formula": "",
                    "interpretation": INTERPRETATIONS.get(rule, ""),
                    "coefficient_relative_to_full_sample": np.nan,
                    "projects_remaining_share": np.nan,
                }
            )
            continue

        sub = _apply_exclusion(base, rule)
        if sub.empty or sub["city"].nunique() < 5:
            rows.append(
                {
                    "exclusion_rule": rule,
                    "spec": spec,
                    "n_cities": int(sub["city"].nunique()) if len(sub) else 0,
                    "n_projects": int(sub["smart_factory_projects"].sum()) if len(sub) else 0,
                    "model": "skipped",
                    "term": "skipped",
                    "coef": "insufficient cities after exclusion",
                    "std_err": np.nan,
                    "p_value": np.nan,
                    "formula": "",
                    "interpretation": INTERPRETATIONS.get(rule, ""),
                    "coefficient_relative_to_full_sample": np.nan,
                    "projects_remaining_share": np.nan,
                }
            )
            continue

        est = fit_ols_table(
            formula,
            sub,
            model=model_name,
            sample_rule=rule,
            fixed_effects="year",
            controls_included=ctrl,
        )
        pilot = est[est["term"] == "pilot_zone"]
        if pilot.empty:
            continue
        p = pilot.iloc[0]
        coef = float(p["coef"])
        n_projects = int(sub["smart_factory_projects"].sum())
        if rule == "full_sample":
            full_coef = coef
            full_projects = n_projects

        rel = coef / full_coef if rule != "full_sample" and full_coef else (1.0 if rule == "full_sample" else np.nan)
        share = n_projects / full_projects if full_projects else np.nan

        rows.append(
            {
                "exclusion_rule": rule,
                "spec": spec,
                "n_cities": int(sub["city"].nunique()),
                "n_projects": n_projects,
                "model": model_name,
                "term": "pilot_zone",
                "coef": coef,
                "std_err": float(p["std_err"]),
                "p_value": float(p["p_value"]),
                "formula": formula,
                "interpretation": INTERPRETATIONS.get(rule, ""),
                "coefficient_relative_to_full_sample": rel,
                "projects_remaining_share": share,
            }
        )

    return pd.DataFrame(rows)


def run_hub_exclusion_robustness(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = add_derived_controls(pd.read_csv(panel_path))

    parts = [_run_spec(panel, spec="baseline", use_controls=False)]
    controlled = _run_spec(panel, spec="controlled", use_controls=True)
    if not controlled.empty:
        parts.append(controlled)

    out = pd.concat(parts, ignore_index=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_6_hub_exclusion_robustness.csv")
    return out
