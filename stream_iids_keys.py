import csv
import shutil
from pathlib import Path

SRC = Path("/root/ai_diffusion_state/data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv")
OUT = Path("/root/ai_diffusion_state/outputs/tables/table_P9_iids_patent_keys_for_geography.csv")
ALIAS = Path("/root/ai_diffusion_state/data/raw/patents/iids_filtered_patent_ids_for_geography.csv")

KEY_COLUMNS = [
    "patent_id",
    "publication_number",
    "applicant_name",
    "patent_title",
    "application_year",
    "publication_year",
    "search_keyword",
]

OUT.parent.mkdir(parents=True, exist_ok=True)
ALIAS.parent.mkdir(parents=True, exist_ok=True)

seen = set()
input_rows = 0
written = 0

with SRC.open("r", encoding="utf-8-sig", errors="replace", newline="") as f_in, OUT.open("w", encoding="utf-8-sig", newline="") as f_out:
    reader = csv.DictReader(f_in)
    writer = csv.DictWriter(f_out, fieldnames=KEY_COLUMNS)
    writer.writeheader()

    for row in reader:
        input_rows += 1
        patent_id = (row.get("patent_id") or "").strip()
        if not patent_id or patent_id in seen:
            continue
        seen.add(patent_id)

        writer.writerow({
            "patent_id": patent_id,
            "publication_number": patent_id,
            "applicant_name": (row.get("applicant_name") or "").strip(),
            "patent_title": (row.get("patent_title") or "").strip(),
            "application_year": (row.get("application_year") or "").strip(),
            "publication_year": (row.get("publication_year") or "").strip(),
            "search_keyword": (row.get("search_keyword") or "").strip(),
        })
        written += 1

        if input_rows % 500000 == 0:
            print({"input_rows": input_rows, "unique_written": written}, flush=True)

shutil.copy2(OUT, ALIAS)

print({"FINAL_input_rows": input_rows, "FINAL_unique_patent_ids": written})
print("Wrote", OUT)
print("Alias", ALIAS)
