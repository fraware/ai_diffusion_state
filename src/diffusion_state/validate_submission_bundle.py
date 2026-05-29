from __future__ import annotations

import json

from diffusion_state.build_submission_bundle import BUNDLE_DIR, BUNDLE_PATHS, MANIFEST_JSON
from diffusion_state.utils import PROJECT_ROOT

REQUIRED_IN_BUNDLE = (
    "draft_v1_submission.md",
    "main_tables/table_A_dataset_counts.csv",
    "main_tables/table_I_appendix_public_fallback_controls.csv",
    "figures/fig_1_diffusion_state_architecture.png",
    "figures/fig_2_hub_attenuation_pilot_coefficients.png",
    "figures/fig_3_city_typology_smart_factory_counts.png",
    "draft_v1_appendix.md",
    "pcs_gate_report.json",
    "references.bib",
    "REPRODUCIBILITY.md",
    "DATA_AVAILABILITY.md",
    "COVER_LETTER_DRAFT.md",
    "SUBMISSION_CHECKLIST.md",
)


def validate_submission_bundle() -> list[str]:
    errors: list[str] = []
    if not BUNDLE_DIR.exists():
        return ["missing paper/submission_bundle/ — run make submission-bundle"]

    if not MANIFEST_JSON.exists():
        errors.append("missing paper/SUBMISSION_MANIFEST.json")

    for name in REQUIRED_IN_BUNDLE:
        if not (BUNDLE_DIR / name).exists():
            errors.append(f"bundle missing: {name}")

    for rel in BUNDLE_PATHS:
        src = PROJECT_ROOT / rel
        if src.exists():
            bundle_name = rel.replace("paper/", "")
            if not (BUNDLE_DIR / bundle_name).exists():
                errors.append(f"bundle out of sync: {bundle_name}")

    if MANIFEST_JSON.exists():
        data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
        if data.get("n_files", 0) < 20:
            errors.append(f"bundle manifest only lists {data.get('n_files')} files (expected 20+)")

    return errors
