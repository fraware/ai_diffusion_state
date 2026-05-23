"""PCS sprint gate summary — single source of truth for paper-ready status."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.geo_evidence import validate_evidence_hygiene
from diffusion_state.panel_controls import city_controls_source
from diffusion_state.smart_factory_overrides import load_city_overrides
from diffusion_state.sync_paper_stats import _filled_audit_decisions, _geo_class_counts, _read_table
from diffusion_state.utils import PROJECT_ROOT

PAPER_TABLES = [
    "table_A_dataset_counts.csv",
    "table_B_city_resolution_quality.csv",
    "table_C_pilot_overlap.csv",
    "table_D_hub_exclusion.csv",
    "table_E_city_typology.csv",
    "table_E_ex_ante_city_typology.csv",
    "table_F_ex_ante_industry_heterogeneity.csv",
    "table_G_export_relevance.csv",
    "table_H_export_sector_share_comparison.csv",
    "table_I_appendix_public_fallback_controls.csv",
]

REQUIRED_SPRINT_TABLES = [
    "table_1_dataset_summary.csv",
    "table_2_top_smart_factory_cities.csv",
    "table_3_pilot_zone_adoption_models.csv",
    "table_6_hub_exclusion_robustness.csv",
    "table_9_city_resolution_audit.csv",
    "table_14_city_diffusion_typology.csv",
    "table_16_geo_evidence_quality.csv",
    "table_timing_diagnostic_coefficients.csv",
]


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str
    severity: str = "error"  # error | warn | info


def _external_verification_count() -> int:
    evq = PROJECT_ROOT / "data" / "interim" / "external_verification_queue.csv"
    if not evq.exists():
        return 0
    q = pd.read_csv(evq)
    urls = q["external_evidence_url"]
    mask = urls.notna() & (urls.astype(str).str.strip() != "") & (urls.astype(str) != "nan")
    return int(mask.sum())


def _table_i_pilot_summary() -> str:
    t = _read_table("table_5b_public_fallback_controls.csv")
    if t is None:
        return "Table I source missing (run make public-fallback-controls)"
    sub = t[(t["term"] == "pilot_zone") & (t["model"].astype(str).str.contains("5b", na=False))]
    if sub.empty:
        return "Table I: pilot_zone row missing"
    row = sub.iloc[0]
    p = float(row["p_value"])
    pstr = "<0.001" if p < 0.001 else f"{p:.3f}"
    return (
        f"Table I OLS count: pilot_zone coef={float(row['coef']):.2f}, p={pstr}, "
        f"N={int(row['n_obs'])}, R2={float(row['r_squared']):.2f} "
        f"(appendix only; not EPS-equivalent)"
    )


def collect_pcs_gates() -> list[GateResult]:
    gates: list[GateResult] = []
    clean_path = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    n_unk = -1
    if clean_path.exists():
        c = pd.read_csv(clean_path)
        n_unk = int((c["city"] == "unknown").sum())
        gates.append(
            GateResult(
                "city_resolution",
                n_unk == 0,
                f"{len(c) - n_unk}/{len(c)} projects resolved ({n_unk} unknown)",
            )
        )

    overrides = load_city_overrides()
    geo_errs = validate_evidence_hygiene(overrides)
    gates.append(
        GateResult(
            "geo_evidence_hygiene",
            not geo_errs,
            "OK" if not geo_errs else f"{len(geo_errs)} hygiene issue(s)",
        )
    )

    official, rule_based, external = _geo_class_counts()
    gates.append(
        GateResult(
            "external_verification",
            external >= 50,
            f"{external} external_evidence_verified (target >= 50)",
            severity="error" if external < 50 else "info",
        )
    )
    gates.append(
        GateResult(
            "geo_evidence_classes",
            True,
            f"official={official}, rule_based={rule_based}, external={external}",
            severity="info",
        )
    )

    audit_path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    if audit_path.exists():
        filled = _filled_audit_decisions(pd.read_csv(audit_path))
        gates.append(
            GateResult(
                "audit_sample",
                filled >= 70,
                f"{filled}/70 auditor_decision filled",
            )
        )
    else:
        gates.append(GateResult("audit_sample", False, "audit CSV missing"))

    n_ext_q = _external_verification_count()
    gates.append(
        GateResult(
            "external_verification_queue",
            n_ext_q >= 50,
            f"{n_ext_q}/50 queue rows with external_evidence_url",
        )
    )

    main_dir = PROJECT_ROOT / "paper" / "main_tables"
    missing_paper = [t for t in PAPER_TABLES if not (main_dir / t).exists()]
    gates.append(
        GateResult(
            "paper_main_tables",
            not missing_paper,
            f"{len(PAPER_TABLES) - len(missing_paper)}/{len(PAPER_TABLES)} tables present"
            + (f"; missing: {', '.join(missing_paper)}" if missing_paper else ""),
        )
    )

    tables_dir = PROJECT_ROOT / "outputs" / "tables"
    missing_sprint = [t for t in REQUIRED_SPRINT_TABLES if not (tables_dir / t).exists()]
    gates.append(
        GateResult(
            "sprint_core_tables",
            not missing_sprint,
            f"{len(REQUIRED_SPRINT_TABLES) - len(missing_sprint)}/{len(REQUIRED_SPRINT_TABLES)} core tables",
        )
    )

    t5 = tables_dir / "table_5_controlled_adoption_models.csv"
    strict_blocked = True
    if t5.exists():
        df = pd.read_csv(t5)
        models = df["model"].astype(str).str.lower()
        strict_blocked = models.str.contains("skipped|controls_missing|missing", regex=True, na=False).any()
        has_model4 = models.str.contains("model_4", na=False).any()
        if has_model4 and not strict_blocked:
            strict_blocked = False
    gates.append(
        GateResult(
            "strict_table_5",
            strict_blocked,
            "skipped by design (expected until EPS/NBS)" if strict_blocked else "model_4_controlled present — verify EPS merge",
            severity="info" if strict_blocked else "warn",
        )
    )

    t5b = tables_dir / "table_5b_public_fallback_controls.csv"
    gates.append(
        GateResult(
            "appendix_table_i",
            t5b.exists() and (main_dir / "table_I_appendix_public_fallback_controls.csv").exists(),
            _table_i_pilot_summary() if t5b.exists() else "Table 5b / Table I missing",
            severity="info" if t5b.exists() else "error",
        )
    )

    src = city_controls_source()
    gates.append(
        GateResult(
            "city_controls_source",
            src == "production",
            f"source={src}; panel merged adoption-year controls: no (expected for public fallback path)",
            severity="info",
        )
    )

    paper_fig_dir = PROJECT_ROOT / "paper" / "figures"
    required_figs = [
        "fig_1_timing_diagnostic_pilot_zones.png",
        "fig_2_city_typology_smart_factory_counts.png",
    ]
    missing_figs = [f for f in required_figs if not (paper_fig_dir / f).exists()]
    gates.append(
        GateResult(
            "paper_figures",
            not missing_figs,
            "main-text figures synced to paper/figures/"
            if not missing_figs
            else f"missing: {', '.join(missing_figs)} (run make paper-figures)",
            severity="error",
        )
    )

    bib = PROJECT_ROOT / "paper" / "references.bib"
    gates.append(
        GateResult(
            "references_bib",
            bib.exists() and bib.read_text(encoding="utf-8").count("@") >= 10,
            f"paper/references.bib ({bib.read_text(encoding='utf-8').count('@')} entries)"
            if bib.exists()
            else "missing paper/references.bib",
            severity="error",
        )
    )

    sub = PROJECT_ROOT / "paper" / "draft_v1_submission.md"
    gates.append(
        GateResult(
            "submission_draft_export",
            sub.exists(),
            "draft_v1_submission.md present" if sub.exists() else "run make export-submission",
            severity="warn",
        )
    )

    tbl_manifest = PROJECT_ROOT / "paper" / "table_manifest.json"
    tables_built = False
    if tbl_manifest.exists():
        import json

        data = json.loads(tbl_manifest.read_text(encoding="utf-8"))
        tables_built = all(t.get("status") == "built" for t in data.get("tables", []))
    gates.append(
        GateResult(
            "paper_tables_embedded",
            tables_built,
            "Tables A–I markdown built in paper/tables_md/"
            if tables_built
            else "run make paper-tables",
            severity="error",
        )
    )

    embedded = sub.exists() and "## Tables (paper/main_tables)" in sub.read_text(encoding="utf-8")
    gates.append(
        GateResult(
            "submission_tables_in_draft",
            embedded,
            "draft_v1_submission.md includes embedded tables"
            if embedded
            else "run make export-submission after paper-tables",
            severity="error",
        )
    )

    bundle_dir = PROJECT_ROOT / "paper" / "submission_bundle"
    gates.append(
        GateResult(
            "submission_bundle",
            bundle_dir.exists() and (bundle_dir / "draft_v1_submission.md").exists(),
            "paper/submission_bundle/ assembled"
            if bundle_dir.exists()
            else "run make submission-bundle",
            severity="error",
        )
    )

    from diffusion_state.validate_draft_claim_compliance import validate_draft_claim_compliance

    claim_issues = validate_draft_claim_compliance()
    gates.append(
        GateResult(
            "draft_claim_compliance",
            not claim_issues,
            "OK" if not claim_issues else f"{len(claim_issues)} issue(s)",
            severity="error",
        )
    )

    return gates


def format_pcs_report(gates: list[GateResult]) -> str:
    lines = ["=== PCS sprint status ===", ""]
    for g in gates:
        mark = "PASS" if g.passed else ("WARN" if g.severity == "warn" else "FAIL")
        lines.append(f"[{mark}] {g.name}: {g.detail}")
    lines.append("")
    lines.append("Paper tables: paper/main_tables/ (Tables A–I)")
    lines.append("Full gate chain: make pcs  (or docs/PCS_GATE_CHECKLIST.md)")
    return "\n".join(lines)


def pcs_ready(gates: list[GateResult] | None = None) -> bool:
    gates = gates or collect_pcs_gates()
    blocking = [g for g in gates if not g.passed and g.severity == "error"]
    return len(blocking) == 0
