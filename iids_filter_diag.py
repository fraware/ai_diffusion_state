from pathlib import Path
from diffusion_state.iids_sql_parser import split_sql_row_tuples, split_sql_tuple_values
from diffusion_state.iids_patent_converter import (
    _is_cn_publication,
    _matches_industrial_ai,
    _load_taxonomy_keywords,
)

SQL = Path("/mnt/iids_sources/Gracie___IIDS/base_patent_detail.sql/base_patent_detail.sql")
TABLE = "base_china_epo_ipc"
COLUMNS = ["row_id","pn","title","abs","pr","ap_or","in_or","ipc","cpc","pn_date","ad","family_number","year"]
KEYWORDS = _load_taxonomy_keywords()

scanned = cn = year_ok = ai = bad_len = 0
limit = 300000

with SQL.open("r", encoding="utf-8", errors="replace") as f:
    for line_no, line in enumerate(f, start=1):
        if TABLE not in line:
            continue
        pos = line.find("VALUES")
        if pos < 0:
            continue
        values = line[pos + len("VALUES"):].strip().rstrip(";")
        for body in split_sql_row_tuples(values):
            vals = split_sql_tuple_values(body)
            if len(vals) != len(COLUMNS):
                bad_len += 1
                if bad_len <= 5:
                    print("BAD_LEN", len(vals), "EXPECTED", len(COLUMNS), "BODY_PREFIX", body[:200])
                continue

            row = dict(zip(COLUMNS, vals))
            scanned += 1

            pn = str(row.get("pn") or "").strip()
            if _is_cn_publication(pn):
                cn += 1

            try:
                y = int(row.get("year"))
            except Exception:
                y = None

            if y is not None and 2015 <= y <= 2024:
                year_ok += 1
                if _is_cn_publication(pn) and _matches_industrial_ai(row, KEYWORDS):
                    ai += 1
                    if ai <= 10:
                        print("AI_HIT", ai, pn, y, str(row.get("title"))[:120], str(row.get("ipc"))[:100])

            if scanned >= limit:
                print({"scanned": scanned, "cn": cn, "year_ok": year_ok, "ai_hits": ai, "bad_len": bad_len})
                raise SystemExit(0)

print({"scanned": scanned, "cn": cn, "year_ok": year_ok, "ai_hits": ai, "bad_len": bad_len})
