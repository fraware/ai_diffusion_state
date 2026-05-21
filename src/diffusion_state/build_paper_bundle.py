from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

PAPER_DIR = PROJECT_ROOT / "paper"
OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"


@dataclass(frozen=True)
class PaperArtifact:
    path: Path
    artifact_type: str
    claim_id: str
    required: bool = True


PAPER_ARTIFACTS: tuple[PaperArtifact, ...] = (
    PaperArtifact(Path("data/processed/pilot_zones.csv"), "processed", "treatment_pilot_zones"),
    PaperArtifact(Path("data/processed/smart_factories_clean.csv"), "processed", "outcome_smart_factories"),
    PaperArtifact(Path("data/processed/smart_factory_city_year.csv"), "processed", "panel_city_year"),
    PaperArtifact(Path("data/processed/analysis_city_year_panel.csv"), "processed", "panel_analysis"),
    PaperArtifact(Path("outputs/tables/table_1_dataset_summary.csv"), "table", "descriptive_data_coverage"),
    PaperArtifact(Path("outputs/tables/table_2_top_smart_factory_cities.csv"), "table", "descriptive_top_cities"),
    PaperArtifact(Path("outputs/tables/table_pilot_zone_overlap.csv"), "table", "descriptive_pilot_overlap_city"),
    PaperArtifact(Path("outputs/tables/table_pilot_zone_province_overlap.csv"), "table", "descriptive_pilot_overlap_province"),
    PaperArtifact(Path("outputs/tables/table_3_pilot_zone_adoption_models.csv"), "table", "models_adoption"),
    PaperArtifact(Path("outputs/tables/table_timing_diagnostic_coefficients.csv"), "table", "timing_diagnostic"),
    PaperArtifact(Path("outputs/figures/fig_timing_diagnostic_pilot_zones.png"), "figure", "fig_timing_diagnostic"),
    PaperArtifact(Path("outputs/tables/table_5_controlled_adoption_models.csv"), "table", "models_controlled", required=False),
    PaperArtifact(Path("outputs/tables/table_6_hub_exclusion_robustness.csv"), "table", "robustness_hub_exclusion"),
    PaperArtifact(Path("outputs/tables/table_7_pilot_city_balance.csv"), "table", "balance_pretreatment", required=False),
    PaperArtifact(Path("outputs/tables/table_8_matched_adoption_models.csv"), "table", "matched_adoption", required=False),
    PaperArtifact(Path("outputs/tables/table_9_city_resolution_audit.csv"), "table", "geo_resolution_audit"),
    PaperArtifact(Path("data/processed/export_outcomes_sector_year.csv"), "processed", "exports_sector_year", required=False),
    PaperArtifact(Path("outputs/tables/table_4_export_upgrading_models.csv"), "table", "models_export_upgrading", required=False),
    PaperArtifact(Path("outputs/tables/table_10_export_bridge_audit.csv"), "table", "export_bridge_audit", required=False),
    PaperArtifact(Path("outputs/tables/table_11_export_sector_descriptives.csv"), "table", "export_sector_descriptives", required=False),
    PaperArtifact(Path("outputs/tables/table_12_export_models_revised.csv"), "table", "export_models_revised", required=False),
    PaperArtifact(Path("outputs/tables/table_13_city_industry_adoption_models.csv"), "table", "city_industry_models"),
    PaperArtifact(Path("data/processed/industry_ai_exposure.csv"), "processed", "industry_ai_exposure", required=False),
    PaperArtifact(Path("data/processed/industry_ai_exposure_ex_ante.csv"), "processed", "industry_ai_exposure_ex_ante"),
    PaperArtifact(Path("outputs/tables/table_14_city_diffusion_typology.csv"), "table", "city_diffusion_typology"),
    PaperArtifact(Path("outputs/figures/fig_city_typology_smart_factory_counts.png"), "figure", "fig_city_typology", required=False),
    PaperArtifact(Path("outputs/tables/table_15_export_relevance_by_sector.csv"), "table", "export_relevance", required=False),
)

CLAIM_MAP_ROWS = [
    {
        "claim_id": "measurement_pilot_zones",
        "claim_tier": "measured",
        "claim_summary": "National AI pilot zones are coded at city/county level with designation years 2019-2021.",
        "artifact": "data/processed/pilot_zones.csv",
        "script": "scripts/00_build_seed_tables.py",
    },
    {
        "claim_id": "measurement_smart_factories",
        "claim_tier": "measured",
        "claim_summary": "MIIT excellence-level smart-factory projects are parsed from 2024 and 2025 public lists.",
        "artifact": "data/processed/smart_factories_clean.csv",
        "script": "scripts/02_parse_smart_factories.py",
    },
    {
        "claim_id": "descriptive_pilot_overlap",
        "claim_tier": "validated_descriptive",
        "claim_summary": "Listed smart-factory recognition is concentrated in pilot-zone cities (resolved cities only).",
        "artifact": "outputs/tables/table_pilot_zone_overlap.csv",
        "script": "scripts/05_run_baseline_models.py",
    },
    {
        "claim_id": "associational_adoption",
        "claim_tier": "controlled_association",
        "claim_summary": "Positive pilot/post-pilot association in baseline models; controlled specs require city_controls_year.csv.",
        "artifact": "outputs/tables/table_3_pilot_zone_adoption_models.csv",
        "script": "src/diffusion_state/run_models.py",
    },
    {
        "claim_id": "controlled_adoption",
        "claim_tier": "controlled_association",
        "claim_summary": "Model 4-7 with city economic controls (blocked until EPS/NBS ingestion).",
        "artifact": "outputs/tables/table_5_controlled_adoption_models.csv",
        "script": "src/diffusion_state/run_controlled_models.py",
    },
    {
        "claim_id": "hub_robustness",
        "claim_tier": "robust_association",
        "claim_summary": "Pilot coefficient collapses outside mega-hubs and direct-admin municipalities.",
        "artifact": "outputs/tables/table_6_hub_exclusion_robustness.csv",
        "script": "src/diffusion_state/run_hub_robustness.py",
    },
    {
        "claim_id": "hub_architecture_typology",
        "claim_tier": "validated_descriptive",
        "claim_summary": "Adoption clusters by diffusion-state city type not pilot binary alone.",
        "artifact": "outputs/tables/table_14_city_diffusion_typology.csv",
        "script": "src/diffusion_state/build_city_diffusion_typology.py",
    },
    {
        "claim_id": "timing_diagnostic",
        "claim_tier": "not_supported",
        "claim_summary": "Pre-2024 bins are mechanical; figure is timing diagnostic only, not pre-trend validation.",
        "artifact": "outputs/tables/table_timing_diagnostic_coefficients.csv",
        "script": "src/diffusion_state/run_models.py",
    },
    {
        "claim_id": "balance_matching",
        "claim_tier": "robust_association",
        "claim_summary": "Pre-treatment balance and matched-sample adoption (requires city controls).",
        "artifact": "outputs/tables/table_7_pilot_city_balance.csv",
        "script": "src/diffusion_state/run_balance_matching.py",
    },
    {
        "claim_id": "city_industry_exposure_ex_ante",
        "claim_tier": "suggestive_mechanism",
        "claim_summary": "Pilot heterogeneity by ex ante industry AI exposure (preferred spec).",
        "artifact": "outputs/tables/table_13_city_industry_adoption_models.csv",
        "script": "src/diffusion_state/run_city_industry_models.py",
    },
    {
        "claim_id": "export_relevance_descriptive",
        "claim_tier": "validated_descriptive",
        "claim_summary": "Smart-factory sectors overlap advanced export basket (no causal claim).",
        "artifact": "outputs/tables/table_15_export_relevance_by_sector.csv",
        "script": "src/diffusion_state/build_export_revised.py",
    },
    {
        "claim_id": "causal_pilot_effect",
        "claim_tier": "not_supported",
        "claim_summary": "Do not claim average pilot-zone treatment effect across treated cities.",
        "artifact": "",
        "script": "",
    },
]


def _artifact_row(artifact: PaperArtifact) -> dict:
    full = PROJECT_ROOT / artifact.path
    row: dict = {
        "path": str(artifact.path).replace("\\", "/"),
        "artifact_type": artifact.artifact_type,
        "claim_id": artifact.claim_id,
        "required": artifact.required,
        "exists": full.exists(),
    }
    if full.exists() and full.suffix.lower() == ".csv":
        df = pd.read_csv(full)
        row["n_rows"] = len(df)
        row["n_cols"] = len(df.columns)
    elif full.exists() and full.suffix.lower() in {".png", ".pdf"}:
        row["n_rows"] = None
        row["n_cols"] = None
        row["bytes"] = full.stat().st_size
    return row


def build_paper_bundle(strict: bool = True) -> dict:
    """Validate paper artifacts and write manifest + claim map under paper/."""
    PAPER_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows = [_artifact_row(a) for a in PAPER_ARTIFACTS]
    missing_required = [
        r["path"] for r in manifest_rows if r["required"] and not r["exists"]
    ]
    if strict and missing_required:
        raise FileNotFoundError(
            "Required paper artifacts missing (run `make analysis` first): "
            + ", ".join(missing_required)
        )

    manifest = {
        "project_root": str(PROJECT_ROOT),
        "artifacts": manifest_rows,
        "missing_required": missing_required,
    }
    manifest_path = PAPER_DIR / "artifact_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    claim_df = pd.DataFrame(CLAIM_MAP_ROWS)
    write_csv(claim_df, PAPER_DIR / "claim_table_map.csv")
    return manifest


if __name__ == "__main__":
    m = build_paper_bundle(strict=True)
    print(f"Wrote {PAPER_DIR / 'artifact_manifest.json'} ({len(m['artifacts'])} artifacts)")
