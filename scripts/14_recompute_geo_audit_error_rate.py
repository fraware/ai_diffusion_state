"""Recompute Table 17 after auditors fill city_resolution_sample_audit.csv."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.build_geo_evidence_quality import build_table_geo_audit_error_rate


def main() -> int:
    build_table_geo_audit_error_rate()
    print("Wrote outputs/tables/table_17_geo_audit_error_rate.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
