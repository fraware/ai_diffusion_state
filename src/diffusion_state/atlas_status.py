from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT
from diffusion_state.validate_atlas_v02 import validate_atlas_v02
from diffusion_state.validate_industry_exposure_v2 import validate_industry_exposure_v2
from diffusion_state.validate_industrial_ai_patents_phase1 import validate_industrial_ai_patents_phase1
from diffusion_state.validate_patent_layer import validate_patent_layer
from diffusion_state.validate_pcs_gates import validate_pcs_gates
from diffusion_state.validate_smart_factory_atlas import validate_smart_factory_city_industry_year

ATLAS_PANEL = PROJECT_ROOT / "data" / "processed" / "china_ai_diffusion_atlas_city_industry_year.csv"
EXPOSURE = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante_v2.csv"
ROBOT = PROJECT_ROOT / "data" / "processed" / "industry_robot_compatibility.csv"
PATENTS = PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
SMART_SF = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
F1 = PROJECT_ROOT / "outputs" / "tables" / "table_F1_pilot_x_ai_exposure_patents.csv"
REPORT_PATH = PROJECT_ROOT / "paper" / "atlas_gate_report.json"


def _pcs_ready() -> bool:
    ok, _ = validate_pcs_gates()
    return ok


def _layer_ready(path: Path, validator_errors: list[str] | None = None) -> bool:
    if not path.exists():
        return False
    if validator_errors is not None and validator_errors:
        return False
    return True


def _main_result_summary() -> str:
    if not F1.exists():
        return "Atlas models not run."
    f1 = pd.read_csv(F1)
    row = f1[(f1["model"] == "pilot_x_ai_exposure_patents_ols_count") & (f1["term"] == "post_x_exposure")]
    if row.empty:
        return "F1 post_x_exposure coefficient not found."
    coef = float(row.iloc[0]["coef"])
    p = row.iloc[0]["p_value"]
    pstr = "n/a" if pd.isna(p) else f"{float(p):.3f}"
    direction = "positive" if coef > 0 else "negative"
    return (
        f"Pilot-zone x AI-exposure -> industrial AI patents (OLS count): "
        f"coef={coef:.4f} ({direction}), p={pstr}. "
        f"Interpret as associational exploratory (saturated FE; fixture patent microdata)."
    )


def _forbidden_claim_flags() -> list[str]:
    flags: list[str] = []
    draft = PROJECT_ROOT / "paper" / "draft_atlas_v1.md"
    if draft.exists():
        text = draft.read_text(encoding="utf-8").lower()
        checks = [
            ("causal treatment effect", "causal_treatment_claim"),
            ("eps/nbs model supports", "eps_equivalent_claim"),
            ("fully audited", "full_audit_overclaim"),
            ("productivity shock proves", "productivity_proof"),
        ]
        for phrase, flag in checks:
            if phrase in text and f"not {phrase.split()[0]}" not in text:
                flags.append(flag)
    return flags


def collect_atlas_status() -> dict:
    exposure_err = validate_industry_exposure_v2()
    patent_err = validate_industrial_ai_patents_phase1()
    pat_ok, _ = validate_patent_layer()
    if not pat_ok:
        patent_err = patent_err + ["legacy patent layer validation failed"]
    sf_err = validate_smart_factory_city_industry_year()
    atlas_err = validate_atlas_v02()

    exposure_ready = _layer_ready(EXPOSURE, exposure_err) and _layer_ready(ROBOT, exposure_err)
    patent_ready = _layer_ready(PATENTS, patent_err)
    sf_ready = _layer_ready(SMART_SF, sf_err)
    panel_ready = _layer_ready(ATLAS_PANEL, atlas_err)
    models_ready = F1.exists() and (PROJECT_ROOT / "outputs" / "tables" / "table_F4_atlas_event_study_patents.csv").exists()

    n_cities = n_industries = years_min = years_max = None
    if ATLAS_PANEL.exists():
        panel = pd.read_csv(ATLAS_PANEL)
        n_cities = int(panel["city"].nunique())
        n_industries = int(panel["industry_code"].nunique())
        years_min = int(panel["year"].min())
        years_max = int(panel["year"].max())

    pcs = _pcs_ready()
    atlas_ready = all([exposure_ready, patent_ready, sf_ready, panel_ready, models_ready])

    return {
        "pcs_ready": pcs,
        "atlas_ready": atlas_ready,
        "exposure_layer_ready": exposure_ready,
        "patent_layer_ready": patent_ready,
        "smart_factory_layer_ready": sf_ready,
        "atlas_panel_ready": panel_ready,
        "atlas_models_ready": models_ready,
        "atlas_phase1_ready": atlas_ready,
        "n_cities": n_cities,
        "n_industries": n_industries,
        "years_min": years_min,
        "years_max": years_max,
        "main_result_summary": _main_result_summary(),
        "forbidden_claim_flags": _forbidden_claim_flags(),
        "layer_errors": {
            "exposure": exposure_err,
            "patents": patent_err,
            "smart_factories": sf_err,
            "atlas_panel": atlas_err,
        },
        "artifact_paths": {
            "industry_crosswalk": "data/seed/industry_crosswalk_atlas.csv",
            "exposure": str(EXPOSURE.relative_to(PROJECT_ROOT)),
            "robot": str(ROBOT.relative_to(PROJECT_ROOT)),
            "patents": str(PATENTS.relative_to(PROJECT_ROOT)),
            "smart_factories": str(SMART_SF.relative_to(PROJECT_ROOT)),
            "atlas_panel": str(ATLAS_PANEL.relative_to(PROJECT_ROOT)),
            "draft_atlas": "paper/draft_atlas_v1.md",
        },
    }


def write_atlas_gate_report(path: Path | None = None) -> dict:
    path = path or REPORT_PATH
    report = collect_atlas_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report
