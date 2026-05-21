"""Print one-page PCS sprint status for paper owner / reviewers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.geo_evidence import validate_evidence_hygiene
from diffusion_state.panel_controls import city_controls_source, controls_available
from diffusion_state.smart_factory_overrides import load_city_overrides
from diffusion_state.utils import PROJECT_ROOT


def main() -> int:
    clean = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    reg = PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    t16 = PROJECT_ROOT / "outputs" / "tables" / "table_16_geo_evidence_quality.csv"
    audit = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    print("=== PCS sprint status ===\n")
    n_unk = -1

    if clean.exists():
        c = pd.read_csv(clean)
        n_unk = int((c["city"] == "unknown").sum())
        print(f"City resolution: {len(c) - n_unk}/{len(c)} resolved ({n_unk} unknown)")

    if reg.exists():
        r = pd.read_csv(reg)
        for rc, n in r["resolution_class"].value_counts().items():
            print(f"  {rc}: {n}")

    overrides = load_city_overrides()
    errs = validate_evidence_hygiene(overrides)
    print(f"Evidence hygiene: {'OK' if not errs else 'FAIL (' + str(len(errs)) + ' issues)'}")

    src = city_controls_source()
    print(f"City controls: {src}")
    panel = PROJECT_ROOT / "data" / "processed" / "analysis_city_year_panel.csv"
    if panel.exists():
        merged = controls_available(pd.read_csv(panel)) and src == "production"
        print(f"Panel controls merged (production): {'yes' if merged else 'no'}")

    evq = PROJECT_ROOT / "data" / "interim" / "external_verification_queue.csv"
    if evq.exists():
        q = pd.read_csv(evq)
        n_ext = int((q["external_evidence_url"].fillna("").astype(str).str.strip() != "").sum())
        print(f"External verification queue: {len(q)} rows ({n_ext} with external_evidence_url)")

    if audit.exists():
        a = pd.read_csv(audit)
        filled = (a["auditor_decision"].fillna("").astype(str).str.strip() != "").sum()
        print(f"Sample audit: {filled}/{len(a)} rows with auditor_decision")

    if t16.exists():
        print(f"Table 16: {t16.relative_to(ROOT)}")

    print("\nPaper tables: paper/main_tables/ (run make main-tables)")
    ok = not errs and clean.exists() and n_unk == 0
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
