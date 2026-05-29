from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

OUTPUT_FIGURES = PROJECT_ROOT / "outputs" / "figures"
PAPER_FIGURES = PROJECT_ROOT / "paper" / "figures"
MANIFEST_PATH = PROJECT_ROOT / "paper" / "figure_manifest.json"


@dataclass(frozen=True)
class PaperFigure:
    output_name: str
    paper_name: str
    claim_id: str
    caption: str
    main_text: bool
    required: bool = True


PCS_FIGURES: tuple[PaperFigure, ...] = (
    PaperFigure(
        "fig_diffusion_state_architecture.png",
        "fig_1_diffusion_state_architecture.png",
        "fig_diffusion_architecture",
        "Conceptual architecture: from frontier AI capability to sectoral and export-relevant industrial adoption.",
        True,
    ),
    PaperFigure(
        "fig_hub_attenuation_pilot_coefficients.png",
        "fig_2_hub_attenuation_pilot_coefficients.png",
        "fig_hub_attenuation",
        "Pilot-zone coefficient on listed smart-factory counts under hub-exclusion rules (95% CI).",
        True,
    ),
    PaperFigure(
        "fig_city_typology_smart_factory_counts.png",
        "fig_3_city_typology_smart_factory_counts.png",
        "fig_city_typology",
        "Listed smart-factory projects by ex ante diffusion-state city type (2024–2025, resolved cities).",
        True,
    ),
    PaperFigure(
        "fig_timing_diagnostic_pilot_zones.png",
        "fig_A2_timing_diagnostic_pilot_zones.png",
        "fig_timing_diagnostic",
        "Timing diagnostic: pilot-zone coefficients by event time (listed smart-factory counts; pre-2024 zeros). Not a pre-trend test.",
        False,
        required=False,
    ),
    PaperFigure(
        "fig_balance_standardized_differences.png",
        "fig_A1_balance_standardized_differences.png",
        "fig_balance",
        "Standardized mean differences for pilot vs non-pilot cities (appendix; controls-dependent).",
        False,
        required=False,
    ),
)


def _ensure_output_figures() -> None:
    """Regenerate PCS figures if missing (requires analysis panel)."""
    OUTPUT_FIGURES.mkdir(parents=True, exist_ok=True)
    arch = OUTPUT_FIGURES / "fig_diffusion_state_architecture.png"
    if not arch.exists():
        from diffusion_state.build_diffusion_architecture_figure import build_diffusion_architecture_figure

        build_diffusion_architecture_figure()
    hub = OUTPUT_FIGURES / "fig_hub_attenuation_pilot_coefficients.png"
    if not hub.exists():
        from diffusion_state.build_hub_attenuation_figure import build_hub_attenuation_figure

        build_hub_attenuation_figure()
    timing = OUTPUT_FIGURES / "fig_timing_diagnostic_pilot_zones.png"
    if not timing.exists():
        from diffusion_state.run_models import run_baseline_models

        run_baseline_models()

    typology = OUTPUT_FIGURES / "fig_city_typology_smart_factory_counts.png"
    if not typology.exists():
        from diffusion_state.build_city_diffusion_typology import build_city_diffusion_typology

        build_city_diffusion_typology()


def build_paper_figures() -> list[dict]:
    _ensure_output_figures()
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    for spec in PCS_FIGURES:
        src = OUTPUT_FIGURES / spec.output_name
        dst = PAPER_FIGURES / spec.paper_name
        if src.exists():
            shutil.copy2(src, dst)
            status = "copied"
        elif spec.required:
            status = "missing"
        else:
            status = "skipped_optional"
        manifest.append(
            {
                "paper_path": f"paper/figures/{spec.paper_name}",
                "source_path": f"outputs/figures/{spec.output_name}",
                "claim_id": spec.claim_id,
                "caption": spec.caption,
                "main_text": spec.main_text,
                "required": spec.required,
                "status": status,
            }
        )

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"figures": manifest}, f, indent=2)
    return manifest
