from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.model_utils import control_terms, fit_ols_table
from diffusion_state.panel_controls import (
    PRE_TREATMENT_YEAR,
    add_derived_controls,
    adoption_sample_with_controls,
    controls_available,
)
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"

BALANCE_COVARIATES = [
    "log_gdp",
    "log_population",
    "secondary_industry_share",
    "industrial_output",
    "fdi",
    "fixed_asset_investment",
    "education_proxy",
    "telecom_or_internet_proxy",
    "foreign_trade",
]


def _std_diff(mean_t: float, mean_c: float, sd_pooled: float) -> float:
    if sd_pooled == 0 or np.isnan(sd_pooled):
        return np.nan
    return (mean_t - mean_c) / sd_pooled


def _balance_row(
    covariate: str,
    treated: pd.Series,
    control: pd.Series,
    matched_t: pd.Series | None = None,
    matched_c: pd.Series | None = None,
) -> dict:
    pooled = np.nanstd(
        pd.concat([treated, control]).astype(float),
        ddof=1,
    )
    row = {
        "covariate": covariate,
        "pilot_mean": float(treated.mean()),
        "non_pilot_mean": float(control.mean()),
        "std_diff_pre": _std_diff(float(treated.mean()), float(control.mean()), pooled),
    }
    if matched_t is not None and matched_c is not None and len(matched_t) and len(matched_c):
        pooled_m = np.nanstd(pd.concat([matched_t, matched_c]).astype(float), ddof=1)
        row["matched_pilot_mean"] = float(matched_t.mean())
        row["matched_non_pilot_mean"] = float(matched_c.mean())
        row["std_diff_matched"] = _std_diff(
            float(matched_t.mean()), float(matched_c.mean()), pooled_m
        )
    else:
        row["matched_pilot_mean"] = np.nan
        row["matched_non_pilot_mean"] = np.nan
        row["std_diff_matched"] = np.nan
    return row


def _nearest_neighbor_match(
    treated: pd.DataFrame,
    control: pd.DataFrame,
    covariates: list[str],
    caliper: float = 0.5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    t = treated.copy()
    c = control.copy()
    used_control: set[int] = set()
    matched_pairs: list[tuple[int, int]] = []

    t_mat = t[covariates].astype(float).values
    c_mat = c[covariates].astype(float).values
    t_std = np.nanstd(t_mat, axis=0, ddof=1)
    t_std[t_std == 0] = 1.0
    t_z = (t_mat - np.nanmean(t_mat, axis=0)) / t_std
    c_z = (c_mat - np.nanmean(t_mat, axis=0)) / t_std

    for i, t_row in enumerate(t_z):
        dists = np.linalg.norm(c_z - t_row, axis=1)
        order = np.argsort(dists)
        for j in order:
            if j in used_control:
                continue
            if dists[j] <= caliper:
                used_control.add(int(j))
                matched_pairs.append((i, int(j)))
                break

    if not matched_pairs:
        return t.iloc[0:0], c.iloc[0:0]

    t_idx = [p[0] for p in matched_pairs]
    c_idx = [p[1] for p in matched_pairs]
    return t.iloc[t_idx].reset_index(drop=True), c.iloc[c_idx].reset_index(drop=True)


def build_pilot_city_balance_2018(panel_path: Path | None = None) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = add_derived_controls(pd.read_csv(panel_path))

    year = PRE_TREATMENT_YEAR
    pre = panel[panel["year"] == year].copy()
    if pre.empty or pre[BALANCE_COVARIATES].notna().sum().sum() == 0:
        years = sorted(panel["year"].unique())
        pre_years = [y for y in years if y < 2024]
        year = pre_years[-1] if pre_years else year
        pre = panel[panel["year"] == year].copy()

    pre = pre.dropna(subset=["city", "pilot_zone"])
    treated = pre[pre["pilot_zone"] == 1]
    control = pre[pre["pilot_zone"] == 0]

    balance_rows = []
    matched_t = matched_c = None
    covs = [c for c in BALANCE_COVARIATES if c in pre.columns]
    usable = [c for c in covs if treated[c].notna().any() and control[c].notna().any()]

    if len(usable) >= 3:
        t_sub = treated.dropna(subset=usable)
        c_sub = control.dropna(subset=usable)
        if len(t_sub) and len(c_sub):
            matched_t, matched_c = _nearest_neighbor_match(t_sub, c_sub, usable)

    for cov in usable:
        balance_rows.append(
            _balance_row(
                cov,
                treated[cov],
                control[cov],
                matched_t[cov] if matched_t is not None and len(matched_t) else None,
                matched_c[cov] if matched_c is not None and len(matched_c) else None,
            )
        )

    balance = pd.DataFrame(balance_rows)
    balance["balance_year"] = year
    out_path = PROJECT_ROOT / "data" / "processed" / "pilot_city_balance_2018.csv"
    write_csv(balance, out_path)

    if matched_t is not None and len(matched_t):
        write_csv(
            pd.concat(
                [
                    matched_t.assign(sample="matched_pilot"),
                    matched_c.assign(sample="matched_control"),
                ]
            ),
            PROJECT_ROOT / "data" / "processed" / "pilot_matched_cities_2018.csv",
        )

    return balance


def _plot_balance(balance: pd.DataFrame, out_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    plot_df = balance.dropna(subset=["std_diff_pre"]).copy()
    if plot_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8, max(4, len(plot_df) * 0.35)))
    y = np.arange(len(plot_df))
    ax.axvline(0, color="gray", linewidth=0.8)
    ax.axvline(-0.25, color="lightgray", linestyle="--", linewidth=0.6)
    ax.axvline(0.25, color="lightgray", linestyle="--", linewidth=0.6)
    ax.scatter(plot_df["std_diff_pre"], y, label="Pre-match", zorder=3)
    if plot_df["std_diff_matched"].notna().any():
        ax.scatter(
            plot_df["std_diff_matched"],
            y,
            marker="s",
            label="Matched",
            zorder=4,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["covariate"])
    ax.set_xlabel("Standardized difference (pilot - non-pilot)")
    ax.set_title("Pilot vs non-pilot city balance")
    ax.legend(loc="lower right")
    fig.tight_layout()
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def run_balance_and_matching(panel_path: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = add_derived_controls(pd.read_csv(panel_path))

    if not panel["gdp"].notna().any():
        skip = pd.DataFrame(
            [
                {
                    "covariate": "skipped",
                    "pilot_mean": np.nan,
                    "non_pilot_mean": np.nan,
                    "std_diff_pre": np.nan,
                    "matched_pilot_mean": np.nan,
                    "matched_non_pilot_mean": np.nan,
                    "std_diff_matched": np.nan,
                    "balance_year": np.nan,
                    "note": "city controls required for balance diagnostics",
                }
            ]
        )
        OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
        write_csv(skip, OUTPUT_TABLES / "table_7_pilot_city_balance.csv")
        write_csv(
            pd.DataFrame([{"term": "skipped", "coef": "controls missing", "model": "matched_adoption"}]),
            OUTPUT_TABLES / "table_8_matched_adoption_models.csv",
        )
        return skip, pd.DataFrame()

    balance = build_pilot_city_balance_2018(panel_path)
    balance_out = balance.copy()
    if "note" not in balance_out.columns:
        balance_out["note"] = ""
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(balance_out, OUTPUT_TABLES / "table_7_pilot_city_balance.csv")
    _plot_balance(balance, OUTPUT_FIGURES / "fig_balance_standardized_differences.png")

    matched_path = PROJECT_ROOT / "data" / "processed" / "pilot_matched_cities_2018.csv"
    matched_results = []
    if matched_path.exists() and controls_available(panel):
        matched_cities = pd.read_csv(matched_path)
        pilot_cities = set(matched_cities.loc[matched_cities["sample"] == "matched_pilot", "city"])
        full = adoption_sample_with_controls(panel)
        sub = full[full["city"].isin(pilot_cities)].copy()
        if len(sub) >= 10:
            formula = f"smart_factory_projects ~ pilot_zone + C(year) + {control_terms()}"
            est = fit_ols_table(
                formula,
                sub,
                model="matched_nn_adoption",
                sample_rule="nearest_neighbor_matched_cities",
                fixed_effects="year",
                controls_included=control_terms(),
            )
            matched_results.append(est)

    if not matched_results:
        matched_out = pd.DataFrame(
            [
                {
                    "term": "skipped",
                    "coef": "matching produced no pairs or controls unavailable",
                    "model": "matched_adoption",
                    "formula": "",
                    "sample_rule": "matched",
                    "n_obs": 0,
                    "n_cities": 0,
                }
            ]
        )
    else:
        matched_out = pd.concat(matched_results, ignore_index=True)

    write_csv(matched_out, OUTPUT_TABLES / "table_8_matched_adoption_models.csv")
    return balance, matched_out
