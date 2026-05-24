"""Machine readiness report for the Atlas IIDS production run."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_geo_join import discover_geography_supplement, is_geography_template_path  # noqa: E402
from diffusion_state.iids_paths import (  # noqa: E402
    DEFAULT_IIDS_OUTPUT,
    MIN_SQL_DOWNLOAD_GB,
    resolve_iids_output_csv,
    resolve_iids_sources_dir,
)
from diffusion_state.iids_patent_converter import find_iids_sql_paths  # noqa: E402
from diffusion_state.patent_raw_sources import MANIFEST_PATH, RAW_PATENTS_DIR  # noqa: E402
from diffusion_state.utils import PROJECT_ROOT  # noqa: E402

OUT_JSON = PROJECT_ROOT / "outputs" / "tables" / "table_P8_iids_machine_readiness.json"


def _disk_free_gb(path: Path) -> float:
    try:
        return shutil.disk_usage(path).free / (1024**3)
    except OSError:
        return 0.0


def _file_rows(path: Path) -> int:
    if not path.exists():
        return 0
    import csv

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return sum(1 for _ in csv.reader(f)) - 1


def _cnipa_or_lens_exports_present() -> bool:
    patterns = ("cnipa_*.csv", "lens_*.csv", "google_patents_*.csv")
    for pattern in patterns:
        for path in RAW_PATENTS_DIR.glob(pattern):
            name = path.name.lower()
            if "template" in name or "geography" in name:
                continue
            return True
    return False


def collect_readiness() -> dict:
    sources = resolve_iids_sources_dir()
    detail, law = find_iids_sql_paths(sources)
    geo = discover_geography_supplement()
    output = resolve_iids_output_csv(production=True)
    free_repo = _disk_free_gb(PROJECT_ROOT)
    free_sources = _disk_free_gb(sources if sources.exists() else sources.parent)

    return {
        "repo_root": str(PROJECT_ROOT),
        "iids_sources_dir": str(sources),
        "disk_free_gb_repo": round(free_repo, 1),
        "disk_free_gb_sources": round(free_sources, 1),
        "min_sql_download_gb": MIN_SQL_DOWNLOAD_GB,
        "openxlab_credentials_set": bool(os.environ.get("OPENXLAB_AK") and os.environ.get("OPENXLAB_SK")),
        "sql_detail_present": detail is not None and detail.exists(),
        "sql_law_present": law is not None and law.exists(),
        "sql_detail_path": str(detail) if detail else "",
        "sql_detail_size_gb": round(detail.stat().st_size / (1024**3), 2) if detail and detail.exists() else 0.0,
        "iids_output_csv": str(output),
        "iids_output_rows": _file_rows(output),
        "geography_supplement": str(geo) if geo else "",
        "geography_is_template": bool(geo and is_geography_template_path(geo)),
        "manifest_present": MANIFEST_PATH.exists(),
        "ready_for_sql_download": free_sources >= MIN_SQL_DOWNLOAD_GB and bool(
            os.environ.get("OPENXLAB_AK") and os.environ.get("OPENXLAB_SK")
        ),
        "ready_for_convert": bool(detail and detail.exists()),
        "ready_for_geography_build": _cnipa_or_lens_exports_present(),
        "ready_for_geography_join": bool(geo and geo.exists() and not is_geography_template_path(geo)),
        "ready_for_evidence_chain": bool(output.exists() and _file_rows(output) >= 500 and geo and not is_geography_template_path(geo)),
        "recommended_next_command": _recommended_next(
            free_sources=free_sources,
            detail=detail,
            output=output,
            geo=geo,
        ),
    }


def _recommended_next(*, free_sources: float, detail: Path | None, output: Path, geo: Path | None) -> str:
    if free_sources < MIN_SQL_DOWNLOAD_GB and (detail is None or not detail.exists()):
        return (
            "Move to a machine with >=150 GB free (or set OPENXLAB_IIDS_SOURCES_DIR to an external drive), "
            "then: python scripts/64_run_atlas_iids_pipeline.py --download --smoke-rows 5000 --production"
        )
    if detail is None or not detail.exists():
        return "python scripts/64_run_atlas_iids_pipeline.py --download --smoke-rows 5000 --production"
    if not output.exists() or _file_rows(output) < 500:
        return "python scripts/64_run_atlas_iids_pipeline.py --skip-geo --production"
    if geo is None or is_geography_template_path(geo):
        return "make atlas-iids-geo-build && make atlas-iids-geo-validate && make atlas-iids-geo"
    return "Complete patent_source_manifest.csv, then: python scripts/64_run_atlas_iids_pipeline.py --full-chain --production"


def main() -> int:
    p = argparse.ArgumentParser(description="Report machine readiness for IIDS production run.")
    p.add_argument("--json", action="store_true")
    p.add_argument("--strict", action="store_true", help="Exit 1 unless ready_for_evidence_chain")
    args = p.parse_args()
    report = collect_readiness()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"IIDS machine readiness -> {OUT_JSON}")
        for key in (
            "disk_free_gb_repo",
            "disk_free_gb_sources",
            "ready_for_sql_download",
            "ready_for_convert",
            "ready_for_geography_join",
            "ready_for_evidence_chain",
            "recommended_next_command",
        ):
            print(f"  {key}: {report[key]}")
    return 0 if not args.strict or report["ready_for_evidence_chain"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
