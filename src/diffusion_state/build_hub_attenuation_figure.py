"""Coefficient plot for pilot-zone hub-exclusion robustness (main-text Figure 2)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"

# Prefer synced main table; fall back to outputs table_6.
TABLE_CANDIDATES = (
    PROJECT_ROOT / "paper" / "main_tables" / "table_D_hub_exclusion.csv",
    OUTPUT_TABLES / "table_6_hub_exclusion_robustness.csv",
)

RULE_ORDER = [
    "full_sample",
    "drop_beijing_shanghai_shenzhen_hangzhou",
    "drop_direct_admin_municipalities",
    "drop_top_5_smart_factory_cities",
]

LABELS = {
    "full_sample": "Full sample",
    "drop_beijing_shanghai_shenzhen_hangzhou": "Drop Beijing, Shanghai,\nShenzhen, Hangzhou",
    "drop_direct_admin_municipalities": "Drop direct-admin\nmunicipalities",
    "drop_top_5_smart_factory_cities": "Drop top five\nsmart-factory cities",
}


def _load_hub_table() -> pd.DataFrame:
    for path in TABLE_CANDIDATES:
        if path.exists():
            return pd.read_csv(path)
    raise FileNotFoundError(f"Hub exclusion table not found in {TABLE_CANDIDATES}")


def build_hub_attenuation_figure() -> Path:
    df = _load_hub_table()
    if "exclusion_rule" not in df.columns and "spec" in df.columns:
        df = df.rename(columns={"spec": "exclusion_rule"})
    sub = df[df["exclusion_rule"].isin(RULE_ORDER)].copy()
    sub["order"] = sub["exclusion_rule"].map({r: i for i, r in enumerate(RULE_ORDER)})
    sub = sub.sort_values("order")
    coef = sub["coef"].astype(float)
    se = sub["std_err"].astype(float)
    labels = [LABELS[r] for r in sub["exclusion_rule"]]

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    y = range(len(sub))
    ax.errorbar(
        coef,
        y,
        xerr=1.96 * se,
        fmt="o",
        color="#1f4e79",
        ecolor="#7a9cb8",
        capsize=4,
        markersize=8,
        linewidth=1.5,
    )
    ax.axvline(coef.iloc[0], color="#c44e52", linestyle="--", linewidth=1, alpha=0.6, label="Full-sample level")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Pilot-zone coefficient (listed smart-factory count)")
    ax.set_title("Hub attenuation: pilot-zone association under city exclusions")
    ax.grid(axis="x", alpha=0.25)
    ax.invert_yaxis()
    fig.tight_layout()

    out = OUTPUT_FIGURES / "fig_hub_attenuation_pilot_coefficients.png"
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(build_hub_attenuation_figure())
