"""Download essential IIDS patent-source files from OpenXLab.

This script intentionally reads credentials from environment variables. Do not commit
OpenXLab access keys, secret keys, passwords, or downloaded proprietary data.

Required environment variables:
    OPENXLAB_AK
    OPENXLAB_SK

Usage, PowerShell:
    $env:OPENXLAB_AK="<your access key>"
    $env:OPENXLAB_SK="<your secret key>"
    python scripts/59_download_iids_patent_sources.py
    python scripts/59_download_iids_patent_sources.py --include-sql

Optional (Windows TLS issues only):
    $env:OPENXLAB_INSECURE_SSL="1"

Outputs:
    data/raw/patents/opendatalab_iids_sources/

After download, run:
    python scripts/60_inspect_iids_patent_schema.py
    python scripts/61_iids_sql_to_patent_csv.py   # when SQL is present locally
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "raw" / "patents" / "opendatalab_iids_sources"
DATASET = "Gracie/IIDS"

DOC_FILES = [
    "/README.md",
    "/metafile.yaml",
    "/Intelligent Innovation Dataset Technical Document.docx",
    "/智创数据库技术文档.docx",
]

SQL_FILES = [
    "/base_patent_detail.sql",
    "/base_patent_law_status.sql",
]


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
    ak = os.environ.get("OPENXLAB_AK")
    sk = os.environ.get("OPENXLAB_SK")
    if not ak or not sk:
        raise SystemExit(
            "Missing OPENXLAB_AK / OPENXLAB_SK environment variables. "
            "Set them locally; do not commit credentials."
        )
    if os.environ.get("OPENXLAB_INSECURE_SSL", "").lower() in ("1", "true", "yes"):
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        import requests

        _orig = requests.Session.request

        def _request(session, method, url, **kwargs):  # noqa: ANN001
            kwargs.setdefault("verify", False)
            return _orig(session, method, url, **kwargs)

        requests.Session.request = _request  # type: ignore[method-assign]
        print("WARNING: OPENXLAB_INSECURE_SSL=1 — TLS certificate verification disabled for this run.")
    import openxlab

    print("Logging in to OpenXLab with environment-provided credentials...")
    openxlab.login(ak=ak, sk=sk)


def _safe_print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="backslashreplace").decode("ascii"))


def download_files(file_list: list[str]) -> None:
    from openxlab.dataset import download

    TARGET.mkdir(parents=True, exist_ok=True)
    for src in file_list:
        _safe_print(f"Downloading {src} -> {TARGET}")
        try:
            download(dataset_repo=DATASET, source_path=src, target_path=str(TARGET))
        except Exception as exc:
            _safe_print(f"FAILED {src}: {exc}")
    _safe_print(f"\nDownloaded files are under: {TARGET}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download IIDS source files from OpenXLab.")
    p.add_argument(
        "--include-sql",
        action="store_true",
        help="Also download base_patent_detail.sql (~136 GB) and base_patent_law_status.sql",
    )
    p.add_argument(
        "--sql-only",
        action="store_true",
        help="Download SQL files only (skip documentation)",
    )
    return p


def main() -> int:
    if sys.platform == "win32":
        os.environ.setdefault("PYTHONUTF8", "1")
    args = _build_parser().parse_args()
    if args.sql_only:
        targets = SQL_FILES
    elif args.include_sql:
        targets = DOC_FILES + SQL_FILES
    else:
        targets = DOC_FILES
        print("Docs-only mode (default). Pass --include-sql on a machine with ~150 GB free disk.")
    ensure_openxlab()
    login()
    download_files(targets)
    print("\nNext command:")
    print("  python scripts/60_inspect_iids_patent_schema.py")
    if args.include_sql or args.sql_only:
        print("  python scripts/61_iids_sql_to_patent_csv.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
