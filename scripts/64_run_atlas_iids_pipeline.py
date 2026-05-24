"""Run the Atlas IIDS patent evidence pipeline with explicit gates."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_paths import (  # noqa: E402
    MIN_SQL_DOWNLOAD_GB,
    resolve_iids_output_csv,
    resolve_iids_sources_dir,
)
from diffusion_state.iids_patent_converter import find_iids_sql_paths  # noqa: E402
from diffusion_state.patent_raw_sources import MANIFEST_PATH, RAW_PATENTS_DIR  # noqa: E402


def _cnipa_or_lens_exports_present() -> bool:
    for pattern in ("cnipa_*.csv", "lens_*.csv", "google_patents_*.csv"):
        for path in RAW_PATENTS_DIR.glob(pattern):
            name = path.name.lower()
            if "template" in name or "geography" in name:
                continue
            return True
    return False


def _run(cmd: list[str], *, label: str) -> int:
    print(f"\n=== {label} ===")
    print(" ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT).returncode


def _disk_free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024**3)


def _preflight(include_sql: bool, sources_dir: Path) -> list[str]:
    issues: list[str] = []
    if include_sql:
        free = _disk_free_gb(sources_dir if sources_dir.exists() else sources_dir.parent)
        if free < MIN_SQL_DOWNLOAD_GB:
            issues.append(
                f"free disk {free:.0f} GB below recommended {MIN_SQL_DOWNLOAD_GB} GB for SQL download; "
                "use --target-dir / OPENXLAB_IIDS_SOURCES_DIR on external storage"
            )
        if not os.environ.get("OPENXLAB_AK") or not os.environ.get("OPENXLAB_SK"):
            issues.append("OPENXLAB_AK / OPENXLAB_SK not set for SQL download")
    detail, _ = find_iids_sql_paths(sources_dir)
    if detail is None:
        issues.append("base_patent_detail.sql not found locally (run download or pass --detail-sql)")
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description="Orchestrate Atlas IIDS patent evidence pipeline.")
    p.add_argument("--download", action="store_true", help="Download IIDS docs + SQL via script 59")
    p.add_argument("--docs-only", action="store_true", help="With --download, skip SQL files")
    p.add_argument("--target-dir", type=Path, default=None, help="IIDS download/SQL directory (external drive)")
    p.add_argument("--smoke-rows", type=int, default=0, help="If >0, run converter with --max-rows")
    p.add_argument("--detail-sql", type=Path, default=None, help="Override base_patent_detail.sql path")
    p.add_argument("--law-status-sql", type=Path, default=None, help="Override base_patent_law_status.sql path")
    p.add_argument("--skip-convert", action="store_true")
    p.add_argument("--cnipa-export", type=Path, default=None, help="Build geography supplement from export")
    p.add_argument("--skip-geo", action="store_true")
    p.add_argument(
        "--production",
        action="store_true",
        help="Write evidence CSV to data/raw/patents/ (required for evidence chain)",
    )
    p.add_argument("--full-chain", action="store_true", help="Run evidence-check, atlas-patents, models, status")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    sources_dir = (args.target_dir or resolve_iids_sources_dir()).resolve()
    if args.target_dir:
        os.environ["OPENXLAB_IIDS_SOURCES_DIR"] = str(sources_dir)

    smoke_mode = args.smoke_rows > 0 and not args.production
    output_csv = resolve_iids_output_csv(production=args.production, smoke=smoke_mode)

    report: dict[str, object] = {
        "steps": [],
        "blockers": [],
        "production": args.production,
        "smoke_mode": smoke_mode,
        "output_csv": str(output_csv),
        "sources_dir": str(sources_dir),
    }

    if args.download:
        cmd = [PYTHON, "scripts/59_download_iids_patent_sources.py", "--target-dir", str(sources_dir)]
        if args.docs_only:
            pass
        else:
            cmd.append("--include-sql")
        code = _run(cmd, label="Download IIDS sources")
        report["steps"].append({"download": code})
        if code == 3:
            report["blockers"].append("insufficient disk for SQL download")
            if args.json:
                print(json.dumps(report, indent=2))
            return code
        if code != 0:
            report["blockers"].append("IIDS download failed")
            if args.json:
                print(json.dumps(report, indent=2))
            return code

    code = _run([PYTHON, "scripts/60_inspect_iids_patent_schema.py"], label="Inspect IIDS schema")
    report["steps"].append({"inspect": code})

    blockers = _preflight(include_sql=False, sources_dir=sources_dir)
    if blockers and not args.skip_convert and not args.detail_sql:
        for b in blockers:
            print(f"PREFLIGHT: {b}", file=sys.stderr)
        report["blockers"].extend(blockers)

    if not args.skip_convert:
        cmd = [PYTHON, "scripts/61_iids_sql_to_patent_csv.py", "--output", str(output_csv)]
        if args.detail_sql:
            cmd.extend(["--detail-sql", str(args.detail_sql)])
        if args.law_status_sql:
            cmd.extend(["--law-status-sql", str(args.law_status_sql)])
        if args.smoke_rows > 0:
            cmd.extend(["--max-rows", str(args.smoke_rows)])
        code = _run(cmd, label="Convert IIDS SQL to patent CSV")
        report["steps"].append({"convert": code})
        if code != 0:
            report["blockers"].append("IIDS conversion failed")
            if args.json:
                print(json.dumps(report, indent=2))
            return code

    if smoke_mode:
        print(f"\nSmoke output (not evidence): {output_csv}")
    elif not output_csv.exists():
        report["blockers"].append(f"missing output {output_csv.name}")
    elif args.production:
        code = _run([PYTHON, "scripts/58_prepare_patent_source_manifest.py"], label="Prepare patent manifest draft")
        report["steps"].append({"manifest_prep": code})

    if not args.skip_geo and args.production:
        if args.cnipa_export or _cnipa_or_lens_exports_present():
            cmd = [PYTHON, "scripts/65_build_patent_geography_from_export.py", "--iids-csv", str(output_csv)]
            if args.cnipa_export:
                cmd.extend(["--export", str(args.cnipa_export)])
            code = _run(cmd, label="Build geography supplement")
            report["steps"].append({"geo_build": code})
            if code not in (0, 3):
                report["blockers"].append("geography build failed")

        cmd = [PYTHON, "scripts/63_validate_patent_geography_supplement.py"]
        code = _run(cmd, label="Validate geography supplement")
        report["steps"].append({"geo_validate": code})
        if code != 0:
            report["blockers"].append("geography supplement below minimum acceptance")

        cmd = [PYTHON, "scripts/62_join_iids_patent_geography.py", "--iids-csv", str(output_csv)]
        code = _run(cmd, label="Join geography to IIDS export")
        report["steps"].append({"geo_join": code})
        if code != 0:
            report["blockers"].append("geography join failed or below minimum acceptance")
    elif not args.skip_geo and smoke_mode:
        print("\nSkipping geography steps in smoke mode (use --production for evidence path).")

    if args.full_chain:
        if not args.production:
            report["blockers"].append("full chain requires --production")
        elif not MANIFEST_PATH.exists():
            report["blockers"].append("patent_source_manifest.csv missing — complete draft before full chain")
        else:
            for target, label in (
                (["make", "atlas-evidence-check"], "Evidence check"),
                (["make", "atlas-patents"], "Atlas patents"),
                (["make", "atlas-v02"], "Atlas v02"),
                (["make", "atlas-models-v02"], "Atlas models"),
            ):
                code = _run(target, label=label)
                report["steps"].append({label.lower().replace(" ", "_"): code})
                if code != 0:
                    report["blockers"].append(f"{label} failed")
            code = _run([PYTHON, "scripts/50_atlas_status.py", "--json"], label="Atlas status")
            report["steps"].append({"status": code})

    if report["blockers"]:
        print("\nBLOCKERS:")
        for b in report["blockers"]:
            print(f"- {b}")
        if args.json:
            print(json.dumps(report, indent=2))
        return 2

    print("\nIIDS pipeline steps completed.")
    if args.production:
        print("Complete patent_source_manifest.csv if not done, then run --full-chain --production")
    if args.json:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
