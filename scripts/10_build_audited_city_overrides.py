"""Generate audited city overrides and rebuild smart-factory tables."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.audited_city_resolution import build_audited_city_overrides
from diffusion_state.build_smart_factories import build_smart_factories_clean
from diffusion_state.utils import PROJECT_ROOT


def main() -> int:
    print("Step 1: rebuild clean with audited geo resolver...")
    build_smart_factories_clean()

    clean = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    import pandas as pd

    before = int((pd.read_csv(clean)["city"] == "unknown").sum())
    print(f"  unknown after geo pass: {before}")

    print("Step 2: write audited overrides for remaining unknown rows...")
    overrides = build_audited_city_overrides(priority_provinces_only=False)
    print(f"  override rows: {len(overrides)}")

    from diffusion_state.apply_geo_workflow_updates import (
        apply_audit_corrections,
        apply_external_verification_queue,
    )

    seed_ext, n_ext = apply_external_verification_queue()
    seed_audit, n_audit = apply_audit_corrections()
    print(f"  external verification rows re-applied: {n_ext}")
    print(f"  audit corrections re-applied: {n_audit}")

    print("Step 3: rebuild clean applying overrides...")
    build_smart_factories_clean()

    clean_df = pd.read_csv(clean)
    after = int((clean_df["city"] == "unknown").sum())
    n = len(clean_df)
    resolved = n - after
    print(f"  resolved city projects: {resolved}/{n}")
    print(f"  remaining unknown: {after}")

    if after > 0:
        print(f"WARN: {after} projects still lack resolved city.")
        return 1
    if len(overrides) < 75:
        print(f"WARN: fewer than 75 override rows ({len(overrides)}).")

    print("==> geo evidence quality tables")
    from diffusion_state.build_geo_evidence_quality import (
        build_city_resolution_register,
        build_geo_sample_audit_template,
        build_table_geo_audit_error_rate,
        build_table_geo_evidence_quality,
    )

    build_city_resolution_register()
    build_table_geo_evidence_quality()
    build_geo_sample_audit_template()
    build_table_geo_audit_error_rate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
