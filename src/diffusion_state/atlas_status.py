from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from diffusion_state.atlas_model_estimation import has_publication_ready_f1
from diffusion_state.utils import PROJECT_ROOT
from diffusion_state.validate_atlas_v02 import validate_atlas_v02
from diffusion_state.validate_industry_exposure_v2 import validate_industry_exposure_v2
from diffusion_state.validate_industrial_ai_patents_phase1 import validate_industrial_ai_patents_phase1
from diffusion_state.validate_no_fixture_patents import (
    collect_evidence_gate_report,
    write_evidence_gate_report,
)
from diffusion_state.validate_patent_layer import validate_patent_layer
from diffusion_state.validate_pcs_gates import validate_pcs_gates
from diffusion_state.validate_smart_factory_atlas import validate_smart_factory_city_industry_year

ATLAS_PANEL = PROJECT_ROOT / "data" / "processed" / "china_ai_diffusion_atlas_city_industry_year.csv"
EXPOSURE = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante_v2.csv"
ROBOT = PROJECT_ROOT / "data" / "processed" / "industry_robot_compatibility.csv"
PATENTS = PROJECT_ROOT / "data" / "processed" / "industrial_ai_patents_city_industry_year.csv"
SMART_SF = PROJECT_ROOT / "data" / "processed" / "smart_factory_city_industry_year.csv"
F1 = PROJECT_ROOT / "outputs" / "tables" / "table_F1_pilot_x_ai_exposure_patents.csv"
F0 = PROJECT_ROOT / "outputs" / "tables" / "table_F0_atlas_model_diagnostics.csv"
REPORT_PATH = PROJECT_ROOT / "paper" / "atlas_gate_report.json"
EVIDENCE_REPORT = PROJECT_ROOT / "paper" / "atlas_evidence_gate_report.json"


def _pcs_ready() -> bool:
    ok, _ = validate_pcs_gates()
    return ok


def _layer_ready(path: Path, validator_errors: list[str] | None = None) -> bool:
    if not path.exists():
        return False
    if validator_errors is not None and validator_errors:
        return False
    return True


def _models_built() -> bool:
    required = (
        F0,
        F1,
        PROJECT_ROOT / "outputs/tables/table_F1a_pilot_x_ai_exposure_patents_baseline.csv",
        PROJECT_ROOT / "outputs/tables/table_F4_atlas_event_study_patents.csv",
    )
    return all(p.exists() for p in required)


def _main_result_summary(evidence: dict) -> str:
    if evidence.get("fixture_patents_detected", True):
        ok, detail = has_publication_ready_f1()
        note = f" (fixture data; exploratory only: {detail})" if ok else ""
        return (
            "Atlas software pipeline operational; patent layer is fixture-backed. "
            "Do not claim pilot-zone x AI-exposure patent association until real CNIPA/Lens exports are ingested."
            + note
        )
    ok, detail = has_publication_ready_f1()
    if ok:
        return f"Publication-ready F1 estimate: {detail}"
    if not F1.exists():
        return "Atlas models not run."
    f1 = pd.read_csv(F1)
    row = f1[(f1["term"].astype(str) == "post_x_exposure")].head(1)
    if row.empty:
        return "F1 post_x_exposure coefficient not found."
    r = row.iloc[0]
    coef = float(r["coef"]) if pd.notna(r["coef"]) else float("nan")
    p = r["p_value"]
    pstr = "n/a" if pd.isna(p) else f"{float(p):.3f}"
    status = r.get("estimator_status", "unknown")
    direction = "positive" if coef > 0 else "negative"
    return (
        f"Pilot-zone x AI-exposure -> industrial AI patents: coef={coef:.4f} ({direction}), "
        f"p={pstr}, estimator_status={status}. "
        f"Not evidence-ready until real CNIPA/Lens patents and valid inference."
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

    evidence = write_evidence_gate_report()

    exposure_ready = _layer_ready(EXPOSURE, exposure_err) and _layer_ready(ROBOT, exposure_err)
    patent_ready = _layer_ready(PATENTS, patent_err) and not evidence.get("fixture_patents_detected", True)
    sf_ready = _layer_ready(SMART_SF, sf_err)
    panel_ready = _layer_ready(ATLAS_PANEL, atlas_err)
    models_built = _models_built()

    models_ready, f1_detail = has_publication_ready_f1()
    if not models_built:
        models_ready = False
        f1_detail = "model tables not built"
    elif evidence.get("fixture_patents_detected", True):
        models_ready = False
        f1_detail = f"fixture patent data - not evidentiary ({f1_detail})"

    n_cities = n_industries = years_min = years_max = None
    if ATLAS_PANEL.exists():
        panel = pd.read_csv(ATLAS_PANEL)
        n_cities = int(panel["city"].nunique())
        n_industries = int(panel["industry_code"].nunique())
        years_min = int(panel["year"].min())
        years_max = int(panel["year"].max())

    pcs = _pcs_ready()
    atlas_software_ready = all([exposure_ready, _layer_ready(PATENTS, patent_err), sf_ready, panel_ready, models_built])
    atlas_evidence_ready = all(
        [
            not evidence.get("fixture_patents_detected", True),
            evidence.get("real_patent_source_present", False),
            patent_ready,
            models_ready,
            not _forbidden_claim_flags(),
        ]
    )
    atlas_ready = atlas_software_ready and atlas_evidence_ready
    atlas_phase1_ready = atlas_ready

    return {
        "pcs_ready": pcs,
        "atlas_ready": atlas_ready,
        "atlas_software_ready": atlas_software_ready,
        "atlas_evidence_ready": atlas_evidence_ready,
        "atlas_phase1_ready": atlas_phase1_ready,
        "fixture_patents_detected": bool(evidence.get("fixture_patents_detected", True)),
        "patent_source_status": evidence.get("patent_source_status", "unknown"),
        "real_patent_source_present": bool(evidence.get("real_patent_source_present", False)),
        "n_raw_patent_records": evidence.get("n_raw_patent_records"),
        "n_unique_patent_ids": evidence.get("n_unique_patent_ids"),
        "exposure_layer_ready": exposure_ready,
        "patent_layer_ready": patent_ready,
        "smart_factory_layer_ready": sf_ready,
        "atlas_panel_ready": panel_ready,
        "atlas_models_built": models_built,
        "atlas_models_ready": models_ready,
        "f1_publication_ready_detail": f1_detail,
        "n_cities": n_cities,
        "n_industries": n_industries,
        "years_min": years_min,
        "years_max": years_max,
        "main_result_summary": _main_result_summary(evidence),
        "forbidden_claim_flags": _forbidden_claim_flags(),
        "layer_errors": {
            "exposure": exposure_err,
            "patents": patent_err,
            "smart_factories": sf_err,
            "atlas_panel": atlas_err,
        },
        "evidence_gate": evidence,
        "artifact_paths": {
            "industry_crosswalk": "data/seed/industry_crosswalk_atlas.csv",
            "exposure": str(EXPOSURE.relative_to(PROJECT_ROOT)),
            "robot": str(ROBOT.relative_to(PROJECT_ROOT)),
            "patents": str(PATENTS.relative_to(PROJECT_ROOT)),
            "smart_factories": str(SMART_SF.relative_to(PROJECT_ROOT)),
            "atlas_panel": str(ATLAS_PANEL.relative_to(PROJECT_ROOT)),
            "evidence_gate_report": "paper/atlas_evidence_gate_report.json",
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
