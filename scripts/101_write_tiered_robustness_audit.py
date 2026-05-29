"""Write P14/P17 tiered robustness tables and audit summary."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geography_gate import collect_iids_geography_gate  # noqa: E402
from diffusion_state.tiered_coverage_tables import (  # noqa: E402
    DEFAULT_GEO,
    DEFAULT_P14,
    DEFAULT_P17_TIERS,
    compute_p14_rows,
    write_p14,
    write_p17_tier_breakdown,
)
from diffusion_state.validate_tiered_robustness import (  # noqa: E402
    validate_tiered_robustness_geography,
    validate_tiered_robustness_panel,
)

DEFAULT_OUT = ROOT / "outputs/tables/table_P17_tiered_robustness_audit.csv"
DEFAULT_JSON = ROOT / "outputs/tables/table_P17_tiered_robustness_audit.json"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--geo", type=Path, default=DEFAULT_GEO)
    p.add_argument("--p14-output", type=Path, default=DEFAULT_P14)
    p.add_argument("--p17-tiers-output", type=Path, default=DEFAULT_P17_TIERS)
    p.add_argument("--output", type=Path, default=DEFAULT_OUT)
    p.add_argument("--json", type=Path, default=DEFAULT_JSON)
    p.add_argument("--skip-p14", action="store_true", help="Use existing P14 on disk")
    args = p.parse_args()

    if not args.geo.exists():
        print(f"ERROR: missing {args.geo}", file=sys.stderr)
        return 1

    if args.skip_p14 and args.p14_output.exists():
        tier_rows = pd.read_csv(args.p14_output, encoding="utf-8-sig").to_dict("records")
        _, n_keys = compute_p14_rows(args.geo)
    else:
        tier_rows, n_keys = write_p14(args.geo, args.p14_output)

    geo_gate = collect_iids_geography_gate()
    fill = float(geo_gate.get("geography_city_fill_rate") or 0.0)
    write_p17_tier_breakdown(
        tier_rows,
        n_keys_total=n_keys,
        overall_city_fill_rate=fill,
        output_path=args.p17_tiers_output,
    )

    panel_ok, panel_issues = validate_tiered_robustness_panel()
    geo_ok, geo_issues = validate_tiered_robustness_geography(geo_gate)
    extension_ready = panel_ok and geo_ok
    evidence_blocked = not bool(geo_gate.get("ready_for_evidence_chain"))

    panel = pd.read_csv(
        ROOT / "data/processed/industrial_ai_patents_city_industry_year.csv",
        encoding="utf-8-sig",
    )
    rows = [
        {"metric": "generated_at_utc", "value": datetime.now(timezone.utc).isoformat()},
        {"metric": "tiered_extension_ready", "value": str(extension_ready)},
        {"metric": "geography_city_fill_rate", "value": geo_gate.get("geography_city_fill_rate")},
        {"metric": "geography_fill_threshold_80pct", "value": geo_gate.get("geography_fill_threshold")},
        {"metric": "tiered_robustness_ready", "value": geo_gate.get("tiered_robustness_ready")},
        {"metric": "ready_for_evidence_chain", "value": geo_gate.get("ready_for_evidence_chain")},
        {"metric": "exact_geography_ready", "value": geo_gate.get("exact_geography_ready")},
        {"metric": "panel_patent_count", "value": int(panel["industrial_ai_patents"].sum())},
        {"metric": "panel_cities", "value": int(panel["city"].nunique())},
        {"metric": "panel_industries", "value": int(panel["industry_code"].nunique())},
        {"metric": "panel_year_min", "value": int(panel["year"].min())},
        {"metric": "panel_year_max", "value": int(panel["year"].max())},
        {"metric": "panel_validation_ok", "value": str(panel_ok)},
        {"metric": "geography_validation_ok", "value": str(geo_ok)},
        {"metric": "publication_f1_blocked", "value": str(evidence_blocked).lower()},
        {"metric": "blockers", "value": "; ".join(panel_issues + geo_issues) or "none"},
        {"metric": "p14_path", "value": str(args.p14_output.relative_to(ROOT))},
        {"metric": "p17_tiers_path", "value": str(args.p17_tiers_output.relative_to(ROOT))},
    ]
    df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False, encoding="utf-8-sig")

    payload = {
        "tiered_extension_ready": extension_ready,
        "publication_f1_blocked": evidence_blocked,
        "geo_gate": {k: geo_gate[k] for k in geo_gate if not str(k).startswith("_")},
        "panel_issues": panel_issues,
        "geo_issues": geo_issues,
        "p14_tiers": tier_rows,
        "artifacts": {
            "p14_csv": str(args.p14_output),
            "p17_tier_breakdown_csv": str(args.p17_tiers_output),
            "p17_audit_csv": str(args.output),
        },
    }
    args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(
        {
            "extension_ready": extension_ready,
            "p14": str(args.p14_output),
            "p17_tiers": str(args.p17_tiers_output),
            "audit": str(args.output),
        }
    )
    return 0 if extension_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
