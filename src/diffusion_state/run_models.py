from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.panel_controls import TIMING_DIAGNOSTIC_NOTE
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"

ADOPTION_YEARS = (2024, 2025)
EVENT_BINS = [-999, -4, -3, -2, -1, 0, 1, 2, 3, 4, 999]
EVENT_LABELS = ["le_m4", "m4", "m3", "m2", "m1", "p0", "p1", "p2", "p3", "ge_p4"]


def _adoption_sample(panel: pd.DataFrame) -> pd.DataFrame:
    return panel[panel["year"].isin(ADOPTION_YEARS)].copy()


def _fit_ols(formula: str, data: pd.DataFrame, cluster: str | None = "city") -> pd.DataFrame:
    model = smf.ols(formula, data=data).fit(
        cov_type="cluster" if cluster else "nonrobust",
        cov_kwds={"groups": data[cluster]} if cluster else None,
    )
    rows = []
    for name, coef in model.params.items():
        rows.append(
            {
                "term": name,
                "coef": coef,
                "std_err": model.bse[name],
                "t_stat": model.tvalues[name],
                "p_value": model.pvalues[name],
                "n_obs": int(model.nobs),
                "r_squared": model.rsquared,
            }
        )
    return pd.DataFrame(rows)


def run_adoption_models(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = pd.read_csv(panel_path)
    sample = _adoption_sample(panel)

    results = []
    specs = [
        (
            "model_1_pilot_zone_indicator",
            "smart_factory_projects ~ pilot_zone + C(year)",
            sample,
        ),
        (
            "model_2_post_pilot_city_year_fe",
            "smart_factory_projects ~ post_pilot + C(city) + C(year)",
            sample,
        ),
        (
            "model_3_log_count_post_pilot",
            "log1p_projects ~ post_pilot + C(city) + C(year)",
            sample.assign(log1p_projects=lambda d: np.log1p(d["smart_factory_projects"])),
        ),
    ]
    for name, formula, data in specs:
        try:
            est = _fit_ols(formula, data)
        except Exception as exc:  # noqa: BLE001 — record failure without synthetic fill
            est = pd.DataFrame(
                [{"term": "error", "coef": str(exc), "std_err": np.nan, "t_stat": np.nan, "p_value": np.nan}]
            )
        est["model"] = name
        est["formula"] = formula
        est["sample_years"] = ",".join(str(y) for y in ADOPTION_YEARS)
        est["n_cities"] = data["city"].nunique()
        results.append(est)

    out = pd.concat(results, ignore_index=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_3_pilot_zone_adoption_models.csv")
    return out


def _event_time_bin(years_since: float) -> str | None:
    if pd.isna(years_since):
        return None
    y = int(years_since)
    if y <= -4:
        return "le_m4"
    if y >= 4:
        return "ge_p4"
    if y == -1:
        return "m1"
    if y == 0:
        return "p0"
    if y == 1:
        return "p1"
    if y == 2:
        return "p2"
    if y == 3:
        return "p3"
    if y == -2:
        return "m2"
    if y == -3:
        return "m3"
    if y == -4:
        return "m4"
    return None


def run_timing_diagnostic(panel_path: Path | None = None) -> tuple[pd.DataFrame, Path | None]:
    """Timing diagnostic on pilot cities; pre-2024 outcomes are zero by construction."""
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = pd.read_csv(panel_path)
    treated = panel[panel["pilot_zone"] == 1].copy()
    treated["event_bin"] = treated["years_since_pilot"].map(_event_time_bin)
    treated = treated[treated["event_bin"].notna() & (treated["event_bin"] != "m1")]

    formula = "smart_factory_projects ~ C(event_bin) + C(city) + C(year)"
    coef_table = _fit_ols(formula, treated)
    coef_table["model"] = "timing_diagnostic_pilot_cities"
    coef_table["reference_bin"] = "m1_omitted"
    coef_table["note"] = TIMING_DIAGNOSTIC_NOTE

    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    table_path = OUTPUT_TABLES / "table_timing_diagnostic_coefficients.csv"
    write_csv(coef_table, table_path)
    legacy_path = OUTPUT_TABLES / "table_event_study_coefficients.csv"
    write_csv(coef_table, legacy_path)

    fig_path = None
    event_coefs = coef_table[
        coef_table["term"].str.startswith("C(event_bin)", na=False)
    ].copy()
    if len(event_coefs) > 0:
        try:
            import matplotlib.pyplot as plt

            event_coefs["bin"] = event_coefs["term"].str.replace("C(event_bin)[T.", "", regex=False).str.rstrip("]")
            order = [b for b in EVENT_LABELS if b in event_coefs["bin"].values]
            plot_df = event_coefs.set_index("bin").loc[order].reset_index()

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.errorbar(
                plot_df["bin"],
                plot_df["coef"],
                yerr=1.96 * plot_df["std_err"],
                fmt="o",
                capsize=4,
            )
            ax.axhline(0, color="gray", linewidth=0.8)
            ax.set_title("Timing diagnostic: smart-factory projects around pilot-zone year")
            ax.set_xlabel("Years since pilot year (ref: -1 omitted)")
            ax.set_ylabel("Coefficient (city and year FE)")
            fig.text(0.01, -0.02, TIMING_DIAGNOSTIC_NOTE, fontsize=7, wrap=True)
            fig.tight_layout()
            OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
            fig_path = OUTPUT_FIGURES / "fig_timing_diagnostic_pilot_zones.png"
            fig.savefig(fig_path, dpi=150)
            legacy_fig = OUTPUT_FIGURES / "fig_event_study_pilot_zones.png"
            shutil.copy(fig_path, legacy_fig)
            plt.close(fig)
        except ImportError:
            fig_path = None

    return coef_table, fig_path


def run_event_study(panel_path: Path | None = None) -> tuple[pd.DataFrame, Path | None]:
    """Backward-compatible alias for timing diagnostic."""
    return run_timing_diagnostic(panel_path)


def run_baseline_models(panel_path: Path | None = None) -> None:
    run_adoption_models(panel_path)
    coefs, fig = run_timing_diagnostic(panel_path)
    print(f"Wrote {OUTPUT_TABLES / 'table_3_pilot_zone_adoption_models.csv'}")
    print(f"Wrote {OUTPUT_TABLES / 'table_timing_diagnostic_coefficients.csv'}")
    if fig:
        print(f"Wrote {fig}")


def run_sprint_analysis(panel_path: Path | None = None) -> None:
    """Baseline plus credibility sprint tables (Steps 3-9)."""
    from diffusion_state.build_export_revised import build_all_export_revised
    from diffusion_state.build_unknown_city_queue import (
        build_city_resolution_audit,
        build_unknown_city_queue,
    )
    from diffusion_state.run_balance_matching import run_balance_and_matching
    from diffusion_state.run_city_industry_models import run_city_industry_adoption_models
    from diffusion_state.run_controlled_models import run_controlled_adoption_models
    from diffusion_state.run_hub_robustness import run_hub_exclusion_robustness

    run_baseline_models(panel_path)
    run_controlled_adoption_models(panel_path)
    run_hub_exclusion_robustness(panel_path)
    run_balance_and_matching(panel_path)
    build_unknown_city_queue()
    build_city_resolution_audit()
    if (PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv").exists():
        try:
            build_all_export_revised()
        except Exception as exc:  # noqa: BLE001
            print(f"Export revised tables skipped: {exc}")
    run_city_industry_adoption_models()


if __name__ == "__main__":
    run_baseline_models()
