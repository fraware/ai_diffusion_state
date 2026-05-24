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
import zipfile

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

DOCX_TABLES = {
    "base_patent_detail": [
        ("pn", "varchar", "Publication (announcement) number"),
        ("title", "text", "Patent title"),
        ("abs", "text", "Abstract"),
        ("pr", "json", "Priority number(s)"),
        ("ap_or", "json", "Applicant name(s)"),
        ("in_or", "json", "Inventor / designer name(s)"),
        ("ipc", "json", "IPC classification codes"),
        ("cpc", "json", "CPC classification codes"),
        ("pn_date", "json", "Publication (announcement) date(s)"),
        ("ad", "json", "Filing / application date(s)"),
        ("family_number", "varchar", "Patent family number"),
        ("year", "int", "Application year"),
    ],
    "base_patent_law_status": [
        ("pn", "varchar", "Patent number (join key to base_patent_detail)"),
        ("event_date", "varchar", "Legal status event date"),
        ("authorize", "int", "Grant effective flag"),
        ("reject", "int", "Rejected / abandoned flag"),
        ("event_code", "varchar", "Legal status code"),
        ("code_expl", "varchar", "Legal status description"),
        ("transfer", "int", "Assignment / transfer flag"),
        ("invalid", "int", "Terminated / expired flag"),
    ],
}

ATLAS_FIELD_MAP = [
    ("patent_id", "partial", "pn", "Publication number, not CN application number"),
    ("application_year", "yes", "year", "Direct int field"),
    ("publication_year", "partial", "pn_date", "Derive year from JSON publication date"),
    ("grant_year", "partial", "base_patent_law_status", "Join on pn; derive from authorize=1 event_date"),
    ("applicant_name", "partial", "ap_or", "JSON list of applicant names only"),
    ("applicant_address", "no", "", "Not documented in base_patent_detail"),
    ("applicant_province", "no", "", "Not documented in base_patent_detail"),
    ("applicant_city", "no", "", "Not documented in base_patent_detail"),
    ("patent_title", "yes", "title", "Direct text field"),
    ("abstract", "yes", "abs", "Direct text field"),
    ("claims_or_description", "no", "", "Claims not documented; abstract only"),
    ("ipc_or_cpc", "yes", "ipc;cpc", "Both JSON fields available"),
    ("patent_type", "no", "", "No patent-kind / type field documented"),
]

HINTS = {
    "id_hint": ["id", "patent", "publication", "application", "公开号", "申请号", "专利", "pn"],
    "date_hint": ["date", "year", "申请日", "公开日", "授权日", "年份", "pn_date", "ad"],
    "applicant_hint": ["applicant", "assignee", "申请人", "权利人", "ap_or"],
    "location_hint": ["address", "province", "city", "地址", "省", "市"],
    "text_hint": ["title", "abstract", "claim", "名称", "摘要", "权利要求", "abs"],
    "class_hint": ["ipc", "cpc", "分类"],
}


def read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
    text = re.sub(r"<[^>]+>", " ", xml)
    return re.sub(r"\s+", " ", text)


def read_sample(path: Path, n: int = 800000) -> str:
    if not path.exists() or path.is_dir():
        return ""
    if path.suffix.lower() == ".docx":
        return read_docx_text(path)
    data = path.read_bytes()[:n]
    for enc in ("utf-8", "utf-8-sig", "gb18030", "gbk", "latin1"):
        try:
            return data.decode(enc, errors="replace")
        except Exception:
            pass
    return data.decode("utf-8", errors="replace")


def column_preview(text: str) -> list[str]:
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
    out = []
    seen = set()
    for x in found:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out[:120]


def docx_table_columns(text: str, table_name: str) -> list[str]:
    if table_name in DOCX_TABLES:
        return [row[0] for row in DOCX_TABLES[table_name]]
    marker = table_name
    idx = text.find(marker)
    if idx < 0:
        return []
    snippet = text[idx : idx + 4000]
    cols = []
    for name, _, _ in re.findall(
        r"\b([a-z_]{2,40})\b\s+(?:varchar|text|json|int)\b", snippet, flags=re.I
    ):
        if name not in cols:
            cols.append(name.lower())
    return cols[:40]


def detect(text: str, cols: list[str]) -> dict[str, bool]:
    blob = (" ".join(cols) + " " + text[:50000]).lower()
    return {k: any(term.lower() in blob for term in terms) for k, terms in HINTS.items()}


def write_inspection_note(
    *,
    sql_detail_present: bool,
    sql_law_present: bool,
    loc_ready: bool,
    text_ready: bool,
    class_ready: bool,
) -> None:
    yes = sum(1 for _, status, _, _ in ATLAS_FIELD_MAP if status == "yes")
    partial = sum(1 for _, status, _, _ in ATLAS_FIELD_MAP if status == "partial")
    missing = sum(1 for _, status, _, _ in ATLAS_FIELD_MAP if status == "no")
    lines = [
        "# IIDS patent schema inspection",
        "",
        f"Files directory: `{SRC}`",
        "",
        "## Download status",
        "",
        f"- `base_patent_detail.sql` present locally: `{sql_detail_present}`",
        f"- `base_patent_law_status.sql` present locally: `{sql_law_present}`",
        "- OpenXLab reports `base_patent_detail.sql` at ~135 GB; full local download is impractical on this machine.",
        "- Schema below is taken from the IIDS technical document (Table 5 / Table 6) when SQL files are absent.",
        "",
        "## base_patent_detail documented fields",
        "",
        "| field | type | description |",
        "| --- | --- | --- |",
    ]
    for name, typ, desc in DOCX_TABLES["base_patent_detail"]:
        lines.append(f"| `{name}` | `{typ}` | {desc} |")
    lines.extend(
        [
            "",
            "## base_patent_law_status documented fields",
            "",
            "| field | type | description |",
            "| --- | --- | --- |",
        ]
    )
    for name, typ, desc in DOCX_TABLES["base_patent_law_status"]:
        lines.append(f"| `{name}` | `{typ}` | {desc} |")
    lines.extend(
        [
            "",
            "## Atlas Phase-1 field coverage",
            "",
            "| atlas_field | coverage | iids_field | notes |",
            "| --- | --- | --- | --- |",
        ]
    )
    for atlas_field, status, iids_field, notes in ATLAS_FIELD_MAP:
        lines.append(f"| `{atlas_field}` | **{status}** | `{iids_field}` | {notes} |")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Direct coverage: `{yes}` fields",
            f"- Partial / join-derived coverage: `{partial}` fields",
            f"- Missing from documented IIDS patent schema: `{missing}` fields",
            f"- Location/address hint detected: `{loc_ready}`",
            f"- Title/abstract/claims hint detected: `{text_ready}`",
            f"- IPC/CPC/classification hint detected: `{class_ready}`",
            "",
            "## Verdict",
            "",
            "`base_patent_detail` is **not sufficient alone** for Atlas evidence ingest because applicant city,",
            "province, and address are not documented. A converter can still produce a partial export for",
            "AI patent classification and year/title/abstract/IPC work, but Atlas `patent_layer_ready` will",
            "remain blocked until applicant geography is joined from another source or confirmed in the SQL dump.",
            "",
            "Next: build a streaming SQL→CSV converter that reads only required columns and filters by year/IPC,",
            "then map to `data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv`.",
        ]
    )
    NOTE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    inv = []
    previews = []
    sql_detail_present = False
    sql_law_present = False
    for name in TARGETS:
        paths = list(SRC.rglob(name)) if SRC.exists() else []
        if not paths:
            inv.append({"file": name, "exists": False, "size_bytes": 0, "path": ""})
            continue
        for p in paths:
            text = read_sample(p)
            if p.suffix.lower() == ".sql":
                cols = column_preview(text)
                if name == "base_patent_detail.sql":
                    sql_detail_present = True
                if name == "base_patent_law_status.sql":
                    sql_law_present = True
            elif p.suffix.lower() == ".docx" and "base_patent_detail" in name.lower():
                cols = docx_table_columns(text, "base_patent_detail")
            elif p.suffix.lower() == ".docx":
                cols = []
                if "base_patent_detail" in text:
                    cols = docx_table_columns(text, "base_patent_detail")
            else:
                cols = []
            hints = detect(text, cols)
            inv.append(
                {
                    "file": name,
                    "exists": True,
                    "size_bytes": p.stat().st_size,
                    "path": str(p.relative_to(ROOT)),
                }
            )
            previews.append(
                {
                    "file": name,
                    "path": str(p.relative_to(ROOT)),
                    "n_column_like_tokens": len(cols),
                    "column_preview": ";".join(cols[:80]),
                    **hints,
                }
            )
    for table_name, rows in DOCX_TABLES.items():
        previews.append(
            {
                "file": f"{table_name} (technical doc Table)",
                "path": "docx:Intelligent Innovation Dataset Technical Document.docx",
                "n_column_like_tokens": len(rows),
                "column_preview": ";".join(name for name, _, _ in rows),
                **detect(" ".join(name for name, _, _ in rows), [name for name, _, _ in rows]),
            }
        )
    pd.DataFrame(inv).to_csv(OUT / "table_P6_iids_file_inventory.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(previews).to_csv(OUT / "table_P7_iids_sql_column_preview.csv", index=False, encoding="utf-8-sig")
    loc_ready = any(r.get("location_hint") for r in previews)
    text_ready = any(r.get("text_hint") for r in previews)
    class_ready = any(r.get("class_hint") for r in previews)
    write_inspection_note(
        sql_detail_present=sql_detail_present,
        sql_law_present=sql_law_present,
        loc_ready=loc_ready,
        text_ready=text_ready,
        class_ready=class_ready,
    )
    print("Wrote IIDS inventory and schema preview tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
