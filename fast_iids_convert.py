from __future__ import annotations

import csv
import io
import json
import os
import re
from pathlib import Path

from diffusion_state.iids_sql_parser import split_sql_row_tuples, split_sql_tuple_values
from diffusion_state.iids_patent_converter import (
    _combine_ipc_cpc,
    _is_cn_publication,
    _json_list_to_text,
    _load_taxonomy_keywords,
    _matches_industrial_ai,
)
from diffusion_state.parse_industrial_ai_patents import PHASE1_COLUMNS

SQL = Path("/mnt/iids_sources/Gracie___IIDS/base_patent_detail.sql/base_patent_detail.sql")
OUT = Path("data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv")
TABLE = "base_patent_detail"

COLUMNS = [
    "row_id",
    "pn",
    "title",
    "abs",
    "pr",
    "ap_or",
    "in_or",
    "ipc",
    "cpc",
    "pn_date",
    "ad",
    "family_number",
    "year",
]

REQUIRE_AI = os.environ.get("IIDS_REQUIRE_AI", "1") != "0"
MAX_INSERT_LINES = int(os.environ.get("IIDS_MAX_INSERT_LINES", "0") or "0")
KEYWORDS = _load_taxonomy_keywords()
OUT.parent.mkdir(parents=True, exist_ok=True)

def first_base_patent_detail_offset(path: Path) -> int:
    marker1 = b"INSERT INTO " + bytes([96]) + b"base_patent_detail" + bytes([96])
    marker2 = b"INSERT INTO base_patent_detail"
    markers = [marker1, marker2]
    chunk_size = 64 * 1024 * 1024
    carry = b""
    offset = 0
    max_marker = max(len(m) for m in markers)

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                raise SystemExit("Could not find base_patent_detail INSERT marker")
            data = carry + chunk
            for marker in markers:
                idx = data.find(marker)
                if idx >= 0:
                    return offset - len(carry) + idx
            offset += len(chunk)
            carry = data[-max_marker:]

def year_from_dates(value):
    try:
        parsed = json.loads(str(value)) if value else []
    except Exception:
        parsed = [str(value)]
    if not isinstance(parsed, list):
        parsed = [str(parsed)]
    for item in parsed:
        m = re.search(r"(20\d{2})", str(item))
        if m:
            return m.group(1)
    return ""

def phase1(row):
    abs_text = str(row.get("abs") or "").strip()
    try:
        app_year = int(row.get("year"))
    except Exception:
        app_year = ""
    return {
        "patent_id": str(row.get("pn") or "").strip(),
        "application_year": str(app_year or ""),
        "publication_year": year_from_dates(row.get("pn_date")),
        "grant_year": "",
        "applicant_name": _json_list_to_text(row.get("ap_or")),
        "applicant_city": "",
        "applicant_province": "",
        "applicant_address": "",
        "patent_title": str(row.get("title") or "").strip(),
        "abstract": abs_text,
        "claims_or_description": abs_text,
        "ipc_or_cpc": _combine_ipc_cpc(row.get("ipc"), row.get("cpc")),
        "patent_type": "",
        "source": "opendatalab_iids",
        "source_url_or_file": "Gracie/IIDS base_patent_detail.sql",
        "search_keyword": "industrial_ai_taxonomy" if REQUIRE_AI else "cn_2015_2024_relaxed",
    }

print("START fast_iids_convert", flush=True)
print("SQL", SQL, SQL.exists(), SQL.stat().st_size if SQL.exists() else None, flush=True)
print("OUT", OUT, flush=True)
print("TABLE", TABLE, flush=True)
print("REQUIRE_AI", REQUIRE_AI, flush=True)

start_offset = first_base_patent_detail_offset(SQL)
print("FIRST_BASE_PATENT_DETAIL_OFFSET", start_offset, flush=True)

scanned = cn_filtered = year_filtered = ai_filtered = written = bad_len = insert_lines = 0

with OUT.open("w", encoding="utf-8-sig", newline="") as f_out:
    writer = csv.DictWriter(f_out, fieldnames=PHASE1_COLUMNS)
    writer.writeheader()

    with SQL.open("rb") as raw:
        raw.seek(start_offset)
        f = io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")

        for relative_line_no, line in enumerate(f, start=1):
            if "INSERT INTO" in line and TABLE not in line and insert_lines > 0:
                print("NEXT_TABLE_REACHED", relative_line_no, flush=True)
                break

            if TABLE not in line:
                continue

            pos = line.find("VALUES")
            if pos < 0:
                continue

            insert_lines += 1
            values = line[pos + len("VALUES"):].strip().rstrip(";")
            row_bodies = split_sql_row_tuples(values)

            print({
                "insert_line": insert_lines,
                "relative_line_no": relative_line_no,
                "row_bodies": len(row_bodies),
                "scanned": scanned,
                "written": written,
            }, flush=True)

            for body in row_bodies:
                vals = split_sql_tuple_values(body)
                if len(vals) != len(COLUMNS):
                    bad_len += 1
                    if bad_len <= 5:
                        print("BAD_LEN", len(vals), "EXPECTED", len(COLUMNS), "BODY_PREFIX", body[:200], flush=True)
                    continue

                row = dict(zip(COLUMNS, vals))
                scanned += 1

                if scanned % 100000 == 0:
                    print({
                        "scanned": scanned,
                        "written": written,
                        "cn_filtered": cn_filtered,
                        "year_filtered": year_filtered,
                        "ai_filtered": ai_filtered,
                        "bad_len": bad_len,
                    }, flush=True)

                pn = str(row.get("pn") or "").strip()
                if not _is_cn_publication(pn):
                    cn_filtered += 1
                    continue

                try:
                    y = int(row.get("year"))
                except Exception:
                    year_filtered += 1
                    continue

                if y < 2015 or y > 2024:
                    year_filtered += 1
                    continue

                if REQUIRE_AI and not _matches_industrial_ai(row, KEYWORDS):
                    ai_filtered += 1
                    continue

                writer.writerow(phase1(row))
                written += 1

                if written <= 10:
                    print("WRITE", written, pn, y, str(row.get("title"))[:120], flush=True)

            f_out.flush()

            if MAX_INSERT_LINES and insert_lines >= MAX_INSERT_LINES:
                print("MAX_INSERT_LINES_REACHED", MAX_INSERT_LINES, flush=True)
                break

print({
    "FINAL_scanned": scanned,
    "FINAL_written": written,
    "cn_filtered": cn_filtered,
    "year_filtered": year_filtered,
    "ai_filtered": ai_filtered,
    "bad_len": bad_len,
}, flush=True)

if scanned == 0:
    raise SystemExit(3)
if written == 0:
    raise SystemExit(4)
