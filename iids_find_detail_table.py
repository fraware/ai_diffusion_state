from pathlib import Path
import re
from diffusion_state.iids_sql_parser import split_sql_row_tuples, split_sql_tuple_values

SQL = Path("/mnt/iids_sources/Gracie___IIDS/base_patent_detail.sql/base_patent_detail.sql")

insert_re = re.compile(r"INSERT\s+INTO\s+[`\"]?([^`\"\s(]+)[`\"]?", re.I)
create_re = re.compile(r"CREATE\s+TABLE\s+[`\"]?([^`\"\s(]+)[`\"]?", re.I)

tables = {}
creates = set()
candidate_13 = []

def inspect_values(line):
    pos = line.find("VALUES")
    if pos < 0:
        return None, None, None
    values = line[pos + len("VALUES"):].strip().rstrip(";")
    bodies = split_sql_row_tuples(values)
    if not bodies:
        return 0, None, None
    vals = split_sql_tuple_values(bodies[0])
    return len(bodies), len(vals), vals[:13]

with SQL.open("r", encoding="utf-8", errors="replace") as f:
    for line_no, line in enumerate(f, start=1):
        cm = create_re.search(line)
        if cm:
            creates.add(cm.group(1))

        im = insert_re.search(line)
        if not im:
            continue

        table = im.group(1)
        if table not in tables:
            n_rows, n_fields, sample = inspect_values(line)
            tables[table] = {
                "first_line": line_no,
                "insert_lines_seen": 0,
                "first_insert_rows": n_rows,
                "first_tuple_fields": n_fields,
                "sample": sample,
            }

        tables[table]["insert_lines_seen"] += 1

        n_rows, n_fields, sample = inspect_values(line)
        if n_fields == 13:
            candidate_13.append((table, line_no, n_rows, sample))
            print("FOUND_13_FIELD_CANDIDATE")
            print("TABLE", table)
            print("LINE", line_no)
            print("ROWS_IN_INSERT", n_rows)
            print("SAMPLE", sample)
            print()

            # Stop after several candidates; enough to identify the correct table.
            if len(candidate_13) >= 5:
                break

        if line_no % 50000 == 0:
            print("PROGRESS_LINE", line_no, "TABLES", list(tables.keys())[:20], flush=True)

print("=== CREATE TABLES SEEN ===")
for t in sorted(creates)[:100]:
    print(t)

print("=== INSERT TABLE INVENTORY ===")
for table, info in tables.items():
    print({
        "table": table,
        "first_line": info["first_line"],
        "insert_lines_seen": info["insert_lines_seen"],
        "first_insert_rows": info["first_insert_rows"],
        "first_tuple_fields": info["first_tuple_fields"],
        "sample": info["sample"],
    })

print("=== 13-FIELD CANDIDATES ===")
for row in candidate_13:
    print(row)
