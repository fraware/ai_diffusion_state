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
    PaperArtifact(Path("outputs/tables/table_event_study_coefficients.csv"), "table", "models_event_study"),
    PaperArtifact(Path("outputs/figures/fig_event_study_pilot_zones.png"), "figure", "fig_event_study"),
    PaperArtifact(Path("data/processed/export_outcomes_sector_year.csv"), "processed", "exports_sector_year", required=False),
    PaperArtifact(Path("outputs/tables/table_4_export_upgrading_models.csv"), "table", "models_export_upgrading", required=False),
)

CLAIM_MAP_ROWS = [
    {
        "claim_id": "measurement_pilot_zones",
        "claim_summary": "National AI pilot zones are coded at city/county level with designation years 2019-2021.",
        "artifact": "data/processed/pilot_zones.csv",
        "script": "scripts/00_build_seed_tables.py",
    },
    {
        "claim_id": "measurement_smart_factories",
        "claim_summary": "MIIT excellence-level smart-factory projects are parsed from 2024 and 2025 public lists.",
        "artifact": "data/processed/smart_factories_clean.csv",
        "script": "scripts/02_parse_smart_factories.py",
    },
    {
        "claim_id": "descriptive_pilot_overlap",
        "claim_summary": "Pilot-zone cities have higher listed smart-factory counts than non-pilot cities (resolved cities only).",
        "artifact": "outputs/tables/table_pilot_zone_overlap.csv",
        "script": "scripts/05_run_baseline_models.py",
    },
    {
        "claim_id": "associational_adoption",
        "claim_summary": "Post-pilot indicator correlates with higher listed adoption in city-year FE models (not causal).",
        "artifact": "outputs/tables/table_3_pilot_zone_adoption_models.csv",
        "script": "src/diffusion_state/run_models.py",
    },
    {
        "claim_id": "event_study_limits",
        "claim_summary": "Event-study bins before 2024 are zero-filled; they do not validate parallel pre-trends.",
        "artifact": "outputs/tables/table_event_study_coefficients.csv",
        "script": "src/diffusion_state/run_models.py",
    },
    {
        "claim_id": "export_upgrading_descriptive",
        "claim_summary": "Sector-year export growth vs smart-factory exposure is descriptive only (optional BACI build).",
        "artifact": "outputs/tables/table_4_export_upgrading_models.csv",
        "script": "src/diffusion_state/build_export_upgrading_tables.py",
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
