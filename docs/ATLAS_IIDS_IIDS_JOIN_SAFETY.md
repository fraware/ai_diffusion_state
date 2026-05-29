# IIDS geography join safety

## In-place join hazard (fixed 2026-05-29)

`scripts/62_join_iids_patent_geography.py` defaults to updating `opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv` in place. On Windows, opening the same path for read and write **truncates** the file immediately, which can destroy a multi-gigabyte export after only a handful of rows.

**Fix:** `join_patent_geography_streaming` now writes to a `.join_tmp` sibling file and atomically replaces the target when joining in place.

**Recovery if the IIDS CSV was truncated:**

**Option A (preferred when `table_P9` exists):** Rebuild from P9 keys + tiered geography (no 10GB re-copy):

```powershell
make atlas-iids-recover-and-robustness
```

Uses `scripts/99_reconstruct_iids_export_from_p9.py` — streams `outputs/tables/table_P9_iids_patent_keys_for_geography.csv` with `cnipa_patent_geography_2015_2024.csv`. Abstract/claims columns are blank until a full SQL re-convert.

**Option B:** Re-copy the full export from the cloud VM:

```powershell
.\scripts\import_iids_copyback.ps1 -Archive path\to\atlas_iids_filtered_outputs.tar.gz
# Expect ~10GB and 4,014,104 data rows
make atlas-iids-geo-tiered-robustness
```
