from __future__ import annotations

from functools import lru_cache

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

CROSSWALK_PATH = PROJECT_ROOT / "data" / "seed" / "industry_crosswalk_atlas.csv"
LEGACY_MAP_PATH = PROJECT_ROOT / "data" / "seed" / "legacy_industry_to_atlas.csv"


@lru_cache(maxsize=1)
def load_legacy_to_atlas() -> dict[str, str]:
    if not LEGACY_MAP_PATH.exists():
        return {}
    df = pd.read_csv(LEGACY_MAP_PATH)
    return dict(zip(df["legacy_industry_code"].astype(str), df["atlas_industry_code"].astype(str)))


def map_legacy_industry_code(legacy_code: str | None) -> str | None:
    if legacy_code is None or (isinstance(legacy_code, float) and pd.isna(legacy_code)):
        return None
    code = str(legacy_code).strip()
    return load_legacy_to_atlas().get(code, code)


def atlas_industry_label(atlas_code: str, crosswalk: pd.DataFrame | None = None) -> str:
    crosswalk = crosswalk if crosswalk is not None else pd.read_csv(CROSSWALK_PATH)
    row = crosswalk[crosswalk["industry_code"] == atlas_code]
    if row.empty:
        return atlas_code
    return str(row.iloc[0]["industry"])
