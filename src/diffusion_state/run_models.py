from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

from diffusion_state.utils import PROJECT_ROOT


def run_baseline_models(panel_path: Path | None = None) -> None:
    panel_path = panel_path or PROJECT_ROOT / "data" / "processed" / "panel_city_year.csv"
    df = pd.read_csv(panel_path)
    if "smart_factory_count" not in df.columns:
        raise ValueError("panel_city_year.csv must contain smart_factory_count")

    # MVP model: treated cities after designation, with city and year fixed effects.
    # Replace C(city_std) with high-dimensional FE estimator if sample is large.
    model = smf.ols(
        "smart_factory_count ~ post_pilot + C(city_std) + C(year)", data=df
    ).fit(cov_type="cluster", cov_kwds={"groups": df["city_std"]})
    print(model.summary())


if __name__ == "__main__":
    run_baseline_models()
