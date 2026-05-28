from pathlib import Path
from diffusion_state.iids_sql_parser import split_sql_row_tuples, split_sql_tuple_values

SQL = Path("/mnt/iids_sources/Gracie___IIDS/base_patent_detail.sql/base_patent_detail.sql")
TABLE = "base_china_epo_ipc"

print("SQL_EXISTS", SQL.exists())
print("SQL_SIZE", SQL.stat().st_size if SQL.exists() else None)

found = False
with SQL.open("r", encoding="utf-8", errors="replace") as f:
    for line_no, line in enumerate(f, start=1):
        if TABLE not in line:
            continue
        found = True
        print("FOUND_LINE", line_no, "LINE_LEN", len(line))
        pos = line.find("VALUES")
        print("VALUES_POS", pos)
        if pos < 0:
            print("NO_VALUES_IN_LINE")
            break
        values = line[pos + len("VALUES"):].strip().rstrip(";")
        bodies = split_sql_row_tuples(values)
        print("ROW_BODIES", len(bodies))
        for i, body in enumerate(bodies[:10], start=1):
            vals = split_sql_tuple_values(body)
            print("ROW", i, "N_FIELDS", len(vals))
            print("FIELDS", vals[:13])
        break

print("FOUND_TABLE_LINE", found)
