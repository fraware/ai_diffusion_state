"""Validate sprint deliverables exist; report city-controls blocker explicitly."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.geo_evidence import validate_evidence_hygiene
from diffusion_state.panel_controls import controls_available
from diffusion_state.smart_factory_overrides import load_city_overrides
from diffusion_state.utils import PROJECT_ROOT
import pandas as pd

REQUIRED_TABLES = [
    "table_1_dataset_summary.csv",
    "table_2_top_smart_factory_cities.csv",
    "table_3_pilot_zone_adoption_models.csv",
    "table_6_hub_exclusion_robustness.csv",
    "table_9_city_resolution_audit.csv",
    "table_14_city_diffusion_typology.csv",
    "table_16_geo_evidence_quality.csv",
    "table_timing_diagnostic_coefficients.csv",
]

PCS_TABLES = [
    "table_17_geo_audit_error_rate.csv",
    "table_18_city_diffusion_typology_ex_ante.csv",
    "table_19_province_year_models.csv",
]

OPTIONAL_TABLES = [
    "table_5_controlled_adoption_models.csv",
    "table_7_pilot_city_balance.csv",
    "table_8_matched_adoption_models.csv",
    "table_10_export_bridge_audit.csv",
    "table_11_export_sector_descriptives.csv",
    "table_12_export_models_revised.csv",
    "table_13_city_industry_adoption_models.csv",
    "table_15_export_relevance_by_sector.csv",
]

BLOCKER = PROJECT_ROOT / "data" / "raw" / "city_controls"
PANEL = PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
STUB_MARKERS = ("city_controls_ci_stub", "STUB_NOTE", "synthetic")


def _is_stub_controls(raw_controls: list[Path]) -> bool:
    if not raw_controls:
        return False
    return all("ci_stub" in p.name.lower() or "stub" in p.name.lower() for p in raw_controls)


def main() -> int:
    tables_dir = PROJECT_ROOT / "outputs" / "tables"
    missing = [t for t in REQUIRED_TABLES if not (tables_dir / t).exists()]
    if missing:
        print("MISSING required tables:", ", ".join(missing))
        return 1

    print("OK required tables:", len(REQUIRED_TABLES))

    pcs_missing = [t for t in PCS_TABLES if not (tables_dir / t).exists()]
    for t in PCS_TABLES:
        path = tables_dir / t
        print(f"  pcs {t}: {'present' if path.exists() else 'absent'}")
    if pcs_missing:
        print("MISSING PCS tables:", ", ".join(pcs_missing))
        return 1

    for t in OPTIONAL_TABLES:
        path = tables_dir / t
        status = "present" if path.exists() else "absent"
        print(f"  optional {t}: {status}")

    from diffusion_state.panel_controls import city_controls_source

    src = city_controls_source()
    if src == "missing":
        print("BLOCKER: no EPS/NBS files in data/raw/city_controls/ — controlled models cannot run.")
    elif src == "stub":
        print("WARN: CI stub city controls — Table 5 not valid for paper claims.")
    else:
        print("OK production city controls source in processed panel.")

    if PANEL.exists():
        panel = pd.read_csv(PANEL)
        if controls_available(panel):
            print("OK city controls merged into analysis panel for adoption years.")
        else:
            print("WARN controls file exists but panel missing adoption-year control values.")

    t5 = tables_dir / "table_5_controlled_adoption_models.csv"
    if t5.exists():
        m = pd.read_csv(t5)
        m4 = m[m["model"].astype(str).str.contains("model_4", na=False)]
        if m4.empty or (m4["term"] == "skipped").all():
            print("Table 5 status: Model 4 skipped (no usable controls).")
        elif (m4["term"] == "error").any():
            print("Table 5 status: Model 4 error — check controls scaling.")
        else:
            pilot = m4[m4["term"] == "pilot_zone"]
            if not pilot.empty:
                p = pilot.iloc[0]
                print(f"Table 5 Model 4 pilot_zone: coef={p['coef']} p={p['p_value']}")
                if src == "stub":
                    print("  (CI stub — do not cite in paper)")
            else:
                print("Table 5 status: Model 4 present without pilot_zone term.")

    t6 = tables_dir / "table_6_hub_exclusion_robustness.csv"
    if t6.exists():
        h = pd.read_csv(t6)
        for col in ("interpretation", "coefficient_relative_to_full_sample", "projects_remaining_share"):
            if col not in h.columns:
                print(f"WARN table_6 missing column: {col}")
        base = h[(h["spec"].astype(str) == "baseline") & (h["exclusion_rule"].astype(str) == "full_sample")]
        if not base.empty and "pilot_zone" in base["term"].values:
            row = base[base["term"] == "pilot_zone"].iloc[0]
            print(f"Table 6 baseline pilot_zone: coef={row['coef']} p={row['p_value']}")

    t16 = tables_dir / "table_16_geo_evidence_quality.csv"
    if t16.exists():
        t = pd.read_csv(t16)
        summary = t[t["evidence_type"] == "_all"]
        if not summary.empty:
            print("Table 16 resolution_class split:")
            for _, r in summary.iterrows():
                print(f"  {r['resolution_class']}: {int(r['n_projects'])} projects")

    overrides = load_city_overrides()
    geo_errors = validate_evidence_hygiene(overrides)
    if geo_errors:
        print("FAIL geo evidence hygiene:")
        for e in geo_errors[:10]:
            print(f"  {e}")
        return 1
    print("OK geo evidence hygiene (overrides)")

    t8_path = tables_dir / "table_8_matched_adoption_models.csv"
    if t8_path.exists():
        t8 = pd.read_csv(t8_path)
        for col in ("n_matched_pilot_cities", "n_matched_control_cities", "matched_city_ratio"):
            if col not in t8.columns:
                print(f"WARN table_8 missing column: {col}")

    ex_ante = PROJECT_ROOT / "data" / "processed" / "industry_ai_exposure_ex_ante.csv"
    if not ex_ante.exists():
        print("WARN missing industry_ai_exposure_ex_ante.csv")

    clean = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    if clean.exists():
        n_unk = int((pd.read_csv(clean)["city"] == "unknown").sum())
        print(f"Unknown-city projects: {n_unk}")
        if n_unk > 0:
            print(f"WARN unknown count {n_unk} (target 0 after geo pass).")
        else:
            print("OK all projects have resolved city.")

    main_tables = PROJECT_ROOT / "paper" / "main_tables"
    if main_tables.exists():
        n = len(list(main_tables.glob("*.csv")))
        print(f"paper/main_tables/: {n} CSV files")
    else:
        print("TIP: run make main-tables after analysis")

    try:
        from diffusion_state.sync_paper_stats import sync_all

        sync_all()
        print("OK paper memos synced from output tables (PCS markers).")
    except ValueError as exc:
        print(f"WARN paper stat sync skipped: {exc}")

    from diffusion_state.validate_audit_sample import validate_audit_sample

    audit_ok, audit_issues = validate_audit_sample()
    if audit_ok:
        print("OK city-resolution audit sample validated")
    else:
        for i in audit_issues:
            print(f"  audit: {i}")

    evq = PROJECT_ROOT / "data" / "interim" / "external_verification_queue.csv"
    if evq.exists():
        print(f"external verification queue: {len(pd.read_csv(evq))} prioritized rows")

    ext_n = 0
    t16 = tables_dir / "table_16_geo_evidence_quality.csv"
    if t16.exists():
        t = pd.read_csv(t16)
        s = t[(t["evidence_type"] == "_all") & (t["resolution_class"] == "external_evidence_verified")]
        if not s.empty:
            ext_n = int(s.iloc[0]["n_projects"])
    print(f"external_evidence_verified projects: {ext_n} (target >=50 for paper)")

    from diffusion_state.validate_pcs_gates import validate_pcs_gates

    pcs_ok, pcs_issues = validate_pcs_gates()
    if pcs_ok:
        print("OK PCS blocking gates (geo, audit, external verification, main tables)")
    else:
        print("FAIL PCS blocking gates:")
        for issue in pcs_issues:
            print(f"  {issue}")
        return 1

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
