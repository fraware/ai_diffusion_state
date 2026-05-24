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

Outputs:
    data/raw/patents/opendatalab_iids_sources/

Downloaded files:
    /README.md
    /metafile.yaml
    /Intelligent Innovation Dataset Technical Document.docx
    /智创数据库技术文档.docx
    /base_patent_detail.sql
    /base_patent_law_status.sql

After download, run:
    python scripts/60_inspect_iids_patent_schema.py
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "raw" / "patents" / "opendatalab_iids_sources"
DATASET = "Gracie/IIDS"

ESSENTIAL_FILES = [
    "/README.md",
    "/metafile.yaml",
    "/Intelligent Innovation Dataset Technical Document.docx",
    "/智创数据库技术文档.docx",
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
    import openxlab

    print("Logging in to OpenXLab with environment-provided credentials...")
    openxlab.login(ak=ak, sk=sk)


def download_files() -> None:
    from openxlab.dataset import download

    TARGET.mkdir(parents=True, exist_ok=True)
    for src in ESSENTIAL_FILES:
        print(f"Downloading {src} -> {TARGET}")
        try:
            download(dataset_repo=DATASET, source_path=src, target_path=str(TARGET))
        except Exception as exc:
            print(f"FAILED {src}: {exc}")
            # Continue so small docs can still be downloaded if one large SQL file fails.
    print(f"\nDownloaded files are under: {TARGET}")


def main() -> int:
    ensure_openxlab()
    login()
    download_files()
    print("\nNext command:")
    print("  python scripts/60_inspect_iids_patent_schema.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
