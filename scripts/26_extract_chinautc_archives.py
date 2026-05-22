"""Extract ChinaUTC China City Statistical Yearbook archives.

This is needed because the public ChinaUTC index often exposes only a few XLSX files,
while the full yearbook RAR contains the remaining tables such as fixed investment,
foreign trade, telecom/post, education, and industrial tables.

Run after scripts/24_fetch_chinautc_city_yearbook.py:

    python scripts/26_extract_chinautc_archives.py --sevenzip "C:\\Program Files\\7-Zip\\7z.exe"

If 7z is on PATH, omit --sevenzip.

Output folders are created next to the archives, for example:

    data/raw/city_controls/chinautc_downloads/2024/extracted_2024_中国城市统计年鉴2024【excel】/
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DL = ROOT / "data" / "raw" / "city_controls" / "chinautc_downloads"


def find_7z(explicit: str | None) -> str:
    candidates = []
    if explicit:
        candidates.append(explicit)
    candidates.extend([
        "7z",
        "7za",
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ])
    for c in candidates:
        if shutil.which(c) or Path(c).exists():
            return c
    raise FileNotFoundError(
        "Could not find 7-Zip. Install 7-Zip and rerun with --sevenzip path, "
        "for example --sevenzip \"C:\\Program Files\\7-Zip\\7z.exe\"."
    )


def extract_archive(archive: Path, sevenzip: str, overwrite: bool = False) -> Path:
    out_dir = archive.parent / f"extracted_{archive.stem}"
    if out_dir.exists() and not overwrite:
        print(f"SKIP exists: {out_dir}")
        return out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sevenzip, "x", str(archive), f"-o{out_dir}", "-y"]
    print("RUN", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sevenzip", default=None, help="Path to 7z.exe or 7z binary")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    sevenzip = find_7z(args.sevenzip)
    archives = sorted(list(DL.rglob("*.rar")) + list(DL.rglob("*.zip")) + list(DL.rglob("*.7z")))
    if not archives:
        print(f"No archives found under {DL}")
        return 1
    for archive in archives:
        try:
            out = extract_archive(archive, sevenzip, overwrite=args.overwrite)
            files = list(out.rglob("*.xlsx")) + list(out.rglob("*.xls"))
            print(f"Extracted {archive.name}: {len(files)} Excel files in {out}")
        except Exception as exc:
            print(f"FAILED {archive}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
