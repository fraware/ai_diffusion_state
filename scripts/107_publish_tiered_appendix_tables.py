"""Copy frozen tiered geography tables into paper/appendix_tables for submission."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = {
    "table_P14_tiered_geography_coverage_by_confidence.csv": ROOT
    / "outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv",
    "table_P17_tiered_geography_tier_breakdown.csv": ROOT
    / "outputs/tables/table_P17_tiered_geography_tier_breakdown.csv",
    "table_P17_tiered_robustness_audit.csv": ROOT
    / "outputs/tables/table_P17_tiered_robustness_audit.csv",
}
OUT_DIR = ROOT / "paper" / "appendix_tables"
README = OUT_DIR / "README.md"


def main() -> int:
    missing = [name for name, path in SRC.items() if not path.exists()]
    if missing:
        print("ERROR: run make atlas-iids-frozen-verify first; missing:", missing, file=sys.stderr)
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, src in SRC.items():
        shutil.copy2(src, OUT_DIR / name)
        print("copied", name)

    README.write_text(
        """# Appendix tables — tiered patent geography (robustness only)

Copied from `outputs/tables/` by `make paper-tiered-appendix-sync`.

- **P14:** coverage by `geo_match_confidence` tier (65.4% overall on 4,014,104 keys).
- **P17:** tier breakdown + audit summary.

Do not describe as exact publication-number geocoding. Not main identification evidence.
See `paper/tiered_patent_geography_methods_snippet.md`.
""",
        encoding="utf-8",
    )
    print("wrote", README)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
