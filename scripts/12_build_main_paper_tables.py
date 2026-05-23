"""Copy paper-critical tables into paper/main_tables/ for drafting."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "main_tables"
SRC = ROOT / "outputs" / "tables"

MAPPING = {
    "table_A_dataset_counts.csv": "table_1_dataset_summary.csv",
    "table_B_city_resolution_quality.csv": "table_16_geo_evidence_quality.csv",
    "table_C_pilot_overlap.csv": "table_pilot_zone_overlap.csv",
    "table_D_hub_exclusion.csv": "table_6_hub_exclusion_robustness.csv",
    "table_E_city_typology.csv": "table_14_city_diffusion_typology.csv",
    "table_E_ex_ante_city_typology.csv": "table_18_city_diffusion_typology_ex_ante.csv",
    "table_F_ex_ante_industry_heterogeneity.csv": "table_13_city_industry_adoption_models.csv",
    "table_G_export_relevance.csv": "table_15_export_relevance_by_sector.csv",
    "table_H_export_sector_share_comparison.csv": "table_export_sector_share_comparison.csv",
    # Appendix-only. This is a partial public-controls robustness table from ChinaUTC.
    # It is deliberately separate from strict Table 5 because FDI and fixed-asset investment
    # are unavailable in the public fallback controls.
    "table_I_appendix_public_fallback_controls.csv": "table_5b_public_fallback_controls.csv",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    claim_src = ROOT / "data" / "seed" / "main_table_claim_map.csv"
    claim_dst = ROOT / "paper" / "main_table_claim_map.csv"
    if claim_src.exists():
        shutil.copy2(claim_src, claim_dst)
    missing = []
    for dest, src_name in MAPPING.items():
        src = SRC / src_name
        if not src.exists():
            missing.append(src_name)
            continue
        shutil.copy2(src, OUT / dest)
    if missing:
        print("MISSING (run make analysis and make public-fallback-controls first):", ", ".join(missing))
        return 1
    print(f"Wrote {len(MAPPING)} tables to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())