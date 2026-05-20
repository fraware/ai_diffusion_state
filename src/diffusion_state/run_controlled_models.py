from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.model_utils import (
    control_terms,
    fit_negative_binomial_table,
    fit_ols_table,
    fit_poisson_table,
)
from diffusion_state.panel_controls import (
    add_derived_controls,
    adoption_sample_with_controls,
    controls_available,
)
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
CONTROLS_STR = control_terms()


def _skipped_table(reason: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "term": "skipped",
                "coef": reason,
                "std_err": np.nan,
                "t_stat": np.nan,
                "p_value": np.nan,
                "n_obs": 0,
                "r_squared": np.nan,
                "model": "controls_missing",
                "formula": "",
                "sample_rule": "none",
                "n_cities": 0,
                "years": "2024,2025",
                "fixed_effects": "",
                "controls_included": "",
            }
        ]
    )


def run_controlled_adoption_models(
    panel_path: Path | None = None,
) -> pd.DataFrame:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    panel = pd.read_csv(panel_path)
    panel = add_derived_controls(panel)

    if not controls_available(panel):
        out = _skipped_table(
            "city_controls_year.csv not merged or adoption-year controls incomplete. "
            "Run make city-controls after placing EPS/NBS files in data/raw/city_controls/."
        )
        OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
        write_csv(out, OUTPUT_TABLES / "table_5_controlled_adoption_models.csv")
        return out

    sample = adoption_sample_with_controls(panel)
    sample = sample.assign(log1p_projects=lambda d: np.log1p(d["smart_factory_projects"]))
    ctrl = CONTROLS_STR
    results: list[pd.DataFrame] = []

    specs = [
        (
            "model_4_controlled_count",
            f"smart_factory_projects ~ pilot_zone + C(year) + {ctrl}",
            sample,
            "year",
            ctrl,
            fit_ols_table,
        ),
        (
            "model_5_controlled_log_count",
            f"log1p_projects ~ pilot_zone + C(year) + {ctrl}",
            sample,
            "year",
            ctrl,
            fit_ols_table,
        ),
    ]
    for name, formula, data, fe, controls, fitter in specs:
        results.append(
            fitter(
                formula,
                data,
                model=name,
                sample_rule="adoption_2024_2025_with_controls",
                fixed_effects=fe,
                controls_included=controls,
            )
        )

    prov_years = sample.groupby("province")["year"].nunique()
    provinces_with_variation = prov_years[prov_years >= 2].index.tolist()
    prov_sample = sample[sample["province"].isin(provinces_with_variation)]
    if len(prov_sample) >= 20 and prov_sample["province"].nunique() >= 3:
        formula6 = f"log1p_projects ~ pilot_zone + C(province):C(year) + {ctrl}"
        try:
            results.append(
                fit_ols_table(
                    formula6,
                    prov_sample,
                    model="model_6_province_year_fe_log",
                    sample_rule="adoption_province_year_fe",
                    fixed_effects="province:year",
                    controls_included=ctrl,
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(
                pd.DataFrame(
                    [
                        {
                            "term": "error",
                            "coef": str(exc),
                            "std_err": np.nan,
                            "t_stat": np.nan,
                            "p_value": np.nan,
                            "n_obs": len(prov_sample),
                            "r_squared": np.nan,
                            "model": "model_6_province_year_fe_log",
                            "formula": formula6,
                            "sample_rule": "adoption_province_year_fe",
                            "n_cities": prov_sample["city"].nunique(),
                            "years": "2024,2025",
                            "fixed_effects": "province:year",
                            "controls_included": ctrl,
                        }
                    ]
                )
            )
    else:
        results.append(
            pd.DataFrame(
                [
                    {
                        "term": "skipped",
                        "coef": "insufficient within-province year variation",
                        "std_err": np.nan,
                        "t_stat": np.nan,
                        "p_value": np.nan,
                        "n_obs": len(prov_sample),
                        "r_squared": np.nan,
                        "model": "model_6_province_year_fe_log",
                        "formula": "",
                        "sample_rule": "adoption_province_year_fe",
                        "n_cities": prov_sample["city"].nunique() if len(prov_sample) else 0,
                        "years": "2024,2025",
                        "fixed_effects": "province:year",
                        "controls_included": ctrl,
                    }
                ]
            )
        )

    formula7 = f"smart_factory_projects ~ pilot_zone + C(year) + {ctrl}"
    results.append(
        fit_poisson_table(
            formula7,
            sample,
            model="model_7_poisson_count",
            sample_rule="adoption_2024_2025_with_controls",
            fixed_effects="year",
            controls_included=ctrl,
        )
    )
    results.append(
        fit_negative_binomial_table(
            formula7,
            sample,
            model="model_7b_negbin_count",
            sample_rule="adoption_2024_2025_with_controls",
            fixed_effects="year",
            controls_included=ctrl,
        )
    )

    out = pd.concat(results, ignore_index=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_5_controlled_adoption_models.csv")
    return out
