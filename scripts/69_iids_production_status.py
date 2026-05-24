"""Write live IIDS production status (WSL download / convert progress)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_production_status import STATUS_JSON, write_production_status  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Report live IIDS production status.")
    p.add_argument("--json", action="store_true")
    p.add_argument("--sources-dir", type=Path, default=None)
    args = p.parse_args()
    report = write_production_status(sources_dir=args.sources_dir)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"IIDS production status -> {STATUS_JSON}")
        for key in (
            "phase",
            "sql_download_pct",
            "sql_detail_size_gb",
            "download_speed",
            "eta_hours",
            "production_active",
            "iids_output_rows",
            "recommended_next",
        ):
            print(f"  {key}: {report.get(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
