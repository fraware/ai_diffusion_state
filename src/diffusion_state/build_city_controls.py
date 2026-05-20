from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

REQUIRED_COLUMNS = [
    "city",
    "province",
    "year",
    "gdp",
    "gdp_per_capita",
    "secondary_value_added",
    "industrial_output",
    "population",
    "employment",
    "average_wage",
    "fdi",
    "fixed_asset_investment",
    "education_proxy",
    "telecom_or_internet_proxy",
    "foreign_trade",
    "source_name",
    "source_file",
]

# EPS / NBS exports must use these English column names after manual rename (documented).
COLUMN_ALIASES = {
    "city_name": "city",
    "city_std": "city",
    "prefecture": "city",
    "province_name": "province",
    "gdp100m": "gdp",
    "gdp_billion_yuan": "gdp",
    "gdp_per_capita_yuan": "gdp_per_capita",
    "secondary_industry_va": "secondary_value_added",
    "industrial_output_value": "industrial_output",
    "total_population": "population",
    "avg_wage": "average_wage",
    "foreign_direct_investment": "fdi",
    "fixed_asset_inv": "fixed_asset_investment",
    "internet_users": "telecom_or_internet_proxy",
    "total_exports_imports": "foreign_trade",
}


def _discover_inputs(raw_dir: Path) -> list[Path]:
    patterns = ["*.csv", "*.xlsx", "*.xls"]
    files: list[Path] = []
    for pat in patterns:
        files.extend(raw_dir.glob(pat))
    return sorted(files)


def build_city_controls_year(
    raw_dir: Path | None = None,
    out_path: Path | None = None,
    missingness_path: Path | None = None,
) -> pd.DataFrame:
    """Build city_controls_year.csv from user-supplied EPS/NBS exports only."""
    raw_dir = raw_dir or PROJECT_ROOT / "data" / "raw" / "city_controls"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"
    missingness_path = (
        missingness_path or PROJECT_ROOT / "data" / "processed" / "city_controls_missingness.csv"
    )

    if not raw_dir.exists():
        raise FileNotFoundError(
            f"No directory {raw_dir}. Place EPS China City Statistics or NBS city tables there. "
            "See docs/source_notes/city_controls.md."
        )

    inputs = _discover_inputs(raw_dir)
    if not inputs:
        raise FileNotFoundError(
            f"No CSV/Excel files in {raw_dir}. See docs/source_notes/city_controls.md."
        )

    frames: list[pd.DataFrame] = []
    for path in inputs:
        if path.suffix.lower() in {".xlsx", ".xls"}:
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
        df = df.rename(columns={c: COLUMN_ALIASES.get(c, c) for c in df.columns})
        df["source_file"] = path.name
        if "source_name" not in df.columns:
            df["source_name"] = "user_supplied"
        frames.append(df)

    out = pd.concat(frames, ignore_index=True)
    missing = [c for c in REQUIRED_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError(
            f"City controls inputs missing required columns: {missing}. "
            f"Found columns: {list(out.columns)}"
        )

    if out.duplicated(subset=["city", "year"]).any():
        dupes = out.loc[out.duplicated(subset=["city", "year"], keep=False), ["city", "year"]]
        raise ValueError(f"Duplicate city-year rows in controls:\n{dupes.head()}")

    miss_rows = []
    for col in REQUIRED_COLUMNS:
        if col in {"city", "province", "year", "source_name", "source_file"}:
            continue
        miss_rows.append(
            {
                "variable": col,
                "share_missing": float(out[col].isna().mean()),
                "n_missing": int(out[col].isna().sum()),
                "n_obs": len(out),
            }
        )
    write_csv(pd.DataFrame(miss_rows), missingness_path)
    write_csv(out[REQUIRED_COLUMNS], out_path)
    return out[REQUIRED_COLUMNS]


if __name__ == "__main__":
    df = build_city_controls_year()
    print(f"Wrote {len(df)} city-year control rows")
