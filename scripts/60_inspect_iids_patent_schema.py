"""Inspect locally downloaded IIDS files for Atlas patent-readiness.

Run after scripts/59_download_iids_patent_sources.py.

Outputs:
  outputs/tables/table_P6_iids_file_inventory.csv
  outputs/tables/table_P7_iids_sql_column_preview.csv
  docs/source_notes/iids_patent_schema_inspection.md
"""
from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "patents" / "opendatalab_iids_sources"
OUT = ROOT / "outputs" / "tables"
NOTE = ROOT / "docs" / "source_notes" / "iids_patent_schema_inspection.md"

TARGETS = [
    "README.md",
    "metafile.yaml",
    "Intelligent Innovation Dataset Technical Document.docx",
    "智创数据库技术文档.docx",
    "base_patent_detail.sql",
    "base_patent_law_status.sql",
]

HINTS = {
    "id_hint": ["id", "patent", "publication", "application", "公开号", "申请号", "专利"],
    "date_hint": ["date", "year", "申请日", "公开日", "授权日", "年份"],
    "applicant_hint": ["applicant", "assignee", "申请人", "权利人"],
    "location_hint": ["address", "province", "city", "地址", "省", "市"],
    "text_hint": ["title", "abstract", "claim", "名称", "摘要", "权利要求"],
    "class_hint": ["ipc", "cpc", "分类"],
}


def read_sample(path: Path, n: int = 800000) -> str:
    if not path.exists() or path.is_dir():
        return ""
    data = path.read_bytes()[:n]
    for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk", "latin1"):
        try:
            return data.decode(enc, errors="replace")
        except Exception:
            pass
    return data.decode("utf-8", errors="replace")


def column_preview(text: str) -> list[str]:
    # Conservative preview: collect backtick/bracket identifiers and early line-start identifiers.
    found = []
    found.extend(re.findall(r"`([^`]{1,80})`", text[:200000]))
    found.extend(re.findall(r"\[([^\]]{1,80})\]", text[:200000]))
    for line in text[:200000].splitlines()[:500]:
        s = line.strip().strip(",")
        if not s or s.startswith(("--", "/*")):
            continue
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]{1,80})\s+", s)
        if m:
            found.append(m.group(1))
    # Deduplicate preserving order.
    out = []
    seen = set()
    for x in found:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out[:120]


def detect(text: str, cols: list[str]) -> dict[str, bool]:
    blob = (" ".join(cols) + " " + text[:50000]).lower()
    return {k: any(term.lower() in blob for term in terms) for k, terms in HINTS.items()}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    inv = []
    previews = []
    for name in TARGETS:
        paths = list(SRC.rglob(name)) if SRC.exists() else []
        if not paths:
            inv.append({"file": name, "exists": False, "size_bytes": 0, "path": ""})
            continue
        for p in paths:
            text = read_sample(p)
            cols = column_preview(text) if p.suffix.lower() == ".sql" else []
            hints = detect(text, cols)
            inv.append({"file": name, "exists": True, "size_bytes": p.stat().st_size, "path": str(p.relative_to(ROOT))})
            previews.append({
                "file": name,
                "path": str(p.relative_to(ROOT)),
                "n_column_like_tokens": len(cols),
                "column_preview": ";".join(cols[:80]),
                **hints,
            })
    pd.DataFrame(inv).to_csv(OUT / "table_P6_iids_file_inventory.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(previews).to_csv(OUT / "table_P7_iids_sql_column_preview.csv", index=False, encoding="utf-8-sig")
    loc_ready = any(r.get("location_hint") for r in previews)
    text_ready = any(r.get("text_hint") for r in previews)
    class_ready = any(r.get("class_hint") for r in previews)
    lines = [
        "# IIDS patent schema inspection",
        "",
        f"Files directory: `{SRC}`",
        f"Location/address hint detected: `{loc_ready}`",
        f"Title/abstract/claims hint detected: `{text_ready}`",
        f"IPC/CPC/classification hint detected: `{class_ready}`",
        "",
        "Next: inspect `outputs/tables/table_P7_iids_sql_column_preview.csv` and map actual SQL fields to the repo patent schema.",
    ]
    NOTE.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote IIDS inventory and schema preview tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
