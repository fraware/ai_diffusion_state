"""Download essential IIDS patent-source files from OpenXLab.

This script intentionally reads credentials from environment variables. Do not commit
OpenXLab access keys, secret keys, passwords, or downloaded proprietary data.

Required environment variables:
    OPENXLAB_AK
    OPENXLAB_SK

Optional:
    OPENXLAB_IIDS_SOURCES_DIR  — download target (use external drive if repo disk is small)
    OPENXLAB_INSECURE_SSL=1    — Windows TLS workaround only

Usage, PowerShell:
    $env:OPENXLAB_AK="<your access key>"
    $env:OPENXLAB_SK="<your secret key>"
    python scripts/59_download_iids_patent_sources.py
    python scripts/59_download_iids_patent_sources.py --include-sql
    python scripts/59_download_iids_patent_sources.py --detail-only --target-dir D:\\iids_sources

Outputs:
    data/raw/patents/opendatalab_iids_sources/  (or --target-dir / OPENXLAB_IIDS_SOURCES_DIR)

After download, run:
    python scripts/60_inspect_iids_patent_schema.py
    python scripts/61_iids_sql_to_patent_csv.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_paths import (  # noqa: E402
    IIDS_DATASET_REPO,
    resolve_iids_download_targets,
    resolve_iids_sources_dir,
    validate_production_target_dir,
)
from diffusion_state.openxlab_client import download_dataset_file, login_openxlab  # noqa: E402

DATASET = IIDS_DATASET_REPO


def run(cmd: list[str], *, hide: bool = False) -> None:
    printable = " ".join(cmd if not hide else [cmd[0], cmd[1], "***"])
    print(f"RUN {printable}")
    subprocess.run(cmd, check=True)


def ensure_openxlab() -> None:
    try:
        import openxlab  # noqa: F401
    except Exception:
        run([sys.executable, "-m", "pip", "install", "-U", "openxlab"])


def login() -> None:
    login_openxlab()


def _safe_print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="backslashreplace").decode("ascii"))


def _disk_free_gb(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.free / (1024**3)


def download_files(file_list: list[str], target: Path) -> int:
    target.mkdir(parents=True, exist_ok=True)
    failures = 0
    for src in file_list:
        _safe_print(f"Downloading {src} -> {target}")
        try:
            download_dataset_file(
                dataset_repo=DATASET,
                source_path=src,
                target_path=target,
                skip_download_check=True,
            )
        except SystemExit as exc:
            _safe_print(f"FAILED {src}: OpenXLab exited ({exc})")
            failures += 1
        except Exception as exc:
            _safe_print(f"FAILED {src}: {exc}")
            failures += 1
    if failures:
        _safe_print(f"\n{failures} download(s) failed under: {target}")
        return 1
    _safe_print(f"\nDownloaded files are under: {target}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download IIDS source files from OpenXLab.")
    p.add_argument(
        "--detail-only",
        action="store_true",
        help="Download only base_patent_detail.sql (~136 GB). Skips law-status and non-patent IIDS files.",
    )
    p.add_argument(
        "--include-sql",
        action="store_true",
        help="Download docs plus both SQL files (detail + law status). Prefer --detail-only under disk pressure.",
    )
    p.add_argument(
        "--sql-only",
        action="store_true",
        help="Download both SQL files only (skip documentation)",
    )
    p.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="Download directory (default: repo opendatalab_iids_sources or OPENXLAB_IIDS_SOURCES_DIR)",
    )
    p.add_argument(
        "--force-sql",
        action="store_true",
        help="Attempt SQL download even when free disk is below the recommended minimum",
    )
    return p


def main() -> int:
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONUTF8", "1")
    args = _build_parser().parse_args()
    if args.detail_only and args.include_sql:
        print("ERROR: use either --detail-only or --include-sql, not both.", file=sys.stderr)
        return 2
    if args.detail_only and args.sql_only:
        print("ERROR: use either --detail-only or --sql-only, not both.", file=sys.stderr)
        return 2

    target = (args.target_dir or resolve_iids_sources_dir()).resolve()
    if args.target_dir:
        os.environ["OPENXLAB_IIDS_SOURCES_DIR"] = str(target)

    wants_sql = args.include_sql or args.sql_only or args.detail_only
    if wants_sql:
        blockers = validate_production_target_dir(target)
        if blockers and not args.force_sql:
            print("ERROR: unsafe download target:", file=sys.stderr)
            for issue in blockers:
                print(f"  - {issue}", file=sys.stderr)
            return 3

    targets = resolve_iids_download_targets(
        include_sql=args.include_sql,
        sql_only=args.sql_only,
        detail_only=args.detail_only,
    )
    if args.detail_only:
        print("Detail-only mode: downloading base_patent_detail.sql only (law status optional at convert time).")
    elif not wants_sql:
        print("Docs-only mode (default). Use --detail-only on external storage for patent SQL.")
    ensure_openxlab()
    login_openxlab()
    code = download_files(targets, target)
    print("\nNext command:")
    print("  python scripts/60_inspect_iids_patent_schema.py")
    if wants_sql:
        print("  python scripts/61_iids_sql_to_patent_csv.py")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
