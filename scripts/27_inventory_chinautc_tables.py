"""Inventory downloaded/extracted ChinaUTC Excel tables.

Run after fetching and extracting archives:

    python scripts/26_extract_chinautc_archives.py --sevenzip "C:\\Program Files\\7-Zip\\7z.exe"
    python scripts/27_inventory_chinautc_tables.py

Output:
    data/raw/city_controls/chinautc_downloads/chinautc_table_inventory.csv
"""
from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DL = ROOT / "data" / "raw" / "city_controls" / "chinautc_downloads"
OUT = DL / "chinautc_table_inventory.csv"

HINTS = {
    "population": ["人口"],
    "gdp": ["地区生产总值"],
    "gdp_composition": ["第二产业", "第三产业", "构成"],
    "employment_wage": ["就业", "工资", "收入"],
    "industrial_output": ["工业企业", "工业总产值", "规模以上工业"],
    "fixed_asset_investment": ["固定资产投资", "Fixed Asset Investment", "全社会固定资产投资"],
    "foreign_trade_fdi": ["进出口", "外商", "外资", "对外经济", "货物进口", "货物出口", "Foreign Trade"],
    "education": ["教育", "学校", "学生"],
    "telecom": ["邮电", "电信", "互联网", "宽带", "移动电话"],
}


def infer_year(path: Path):
    hit = re.search(r"20[0-9][0-9]", str(path))
    return int(hit.group(0)) if hit else None


def infer_code(path: Path):
    name = path.name.replace("_", "-")
    hit = re.search(r"(?:20[0-9][0-9]-)?([23]-[0-9]{1,2})", name)
    return hit.group(1) if hit else ""


def read_preview(path: Path):
    try:
        df = pd.read_excel(path, header=None, nrows=12, dtype=object)
    except Exception as exc:
        return "READ_ERROR " + str(exc)
    vals = []
    for item in df.fillna("").astype(str).values.ravel().tolist():
        item = item.strip()
        if item:
            vals.append(item)
    return " | ".join(vals[:60])


def classify(text: str, filename: str):
    blob = filename + " " + text
    hits = []
    for label, needles in HINTS.items():
        if any(n in blob for n in needles):
            hits.append(label)
    return "|".join(hits)


def main():
    if not DL.exists():
        raise FileNotFoundError(f"Missing {DL}")
    files = sorted(list(DL.rglob("*.xlsx")) + list(DL.rglob("*.xls")))
    rows = []
    for path in files:
        preview = read_preview(path)
        rows.append({
            "year": infer_year(path),
            "table_code": infer_code(path),
            "filename": path.name,
            "relative_path": str(path.relative_to(DL)),
            "size_bytes": path.stat().st_size,
            "hints": classify(preview, path.name),
            "preview": preview[:1000],
        })
    pd.DataFrame(rows).to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(rows)} rows to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
