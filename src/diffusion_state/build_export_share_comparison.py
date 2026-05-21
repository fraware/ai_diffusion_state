"""Compact smart-factory vs export-basket sector shares (descriptive, Engineer C)."""
from __future__ import annotations

import pandas as pd

from diffusion_state.build_export_revised import build_export_relevance_by_sector
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"


def build_export_sector_share_comparison() -> pd.DataFrame:
    base = build_export_relevance_by_sector()
    out = base[
        [
            "sector_group",
            "smart_factory_projects",
            "share_of_smart_factory_projects",
            "share_of_china_exports_2024",
            "mapping_confidence",
            "log_export_growth_2017_2024",
        ]
    ].copy()
    out["share_gap_sf_minus_export"] = (
        out["share_of_smart_factory_projects"] - out["share_of_china_exports_2024"]
    )
    out = out.sort_values("share_gap_sf_minus_export", ascending=False)
    out["note"] = (
        "Descriptive comparison of listed smart-factory sector mix vs 2024 export basket; "
        "not causal."
    )
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_export_sector_share_comparison.csv")
    return out
