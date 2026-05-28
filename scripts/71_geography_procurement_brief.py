"""Generate a geography procurement brief from filtered IIDS patent keys."""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from diffusion_state.iids_paths import FILTERED_PATENT_IDS_FOR_GEO_OUTPUT, PATENT_KEYS_FOR_GEO_OUTPUT  # noqa: E402

OUT_MD = ROOT / "docs" / "ATLAS_IIDS_GEOGRAPHY_PROCUREMENT_BRIEF.md"
BATCH_DIR = ROOT / "data" / "interim" / "iids_geo_key_batches"


def _summarize_keys(keys_csv: Path) -> tuple[int, int, int]:
    n = 0
    year_min = 9999
    year_max = 0
    with keys_csv.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n += 1
            try:
                y = int(str(row.get("application_year", "")).strip())
            except ValueError:
                continue
            year_min = min(year_min, y)
            year_max = max(year_max, y)
    if n == 0:
        return 0, 0, 0
    if year_min == 9999:
        year_min = 0
    return n, year_min, year_max


def build_brief(keys_csv: Path) -> str:
    n, year_min, year_max = _summarize_keys(keys_csv)
    batch_count = len(list(BATCH_DIR.glob("iids_geo_keys_batch_*.csv"))) if BATCH_DIR.exists() else 0
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")

    return f"""# Atlas IIDS geography procurement brief

Generated: {ts}

Source keys file: `{keys_csv.relative_to(ROOT).as_posix()}`

## Request

Export **address metadata only** for the publication numbers in the keys file. Do not download a full patent universe.

| Metric | Value |
|--------|-------|
| Unique patent IDs | {n:,} |
| Application years | {year_min}–{year_max} |
| Pre-chunked batch files | {batch_count} (`data/interim/iids_geo_key_batches/`) |

## Required output file

Place on the control laptop:

```text
data/raw/patents/cnipa_patent_geography_2015_2024.csv
```

Intermediate concatenated export (do not treat as final until normalized):

```text
data/raw/patents/cnipa_patent_geography_2015_2024_raw.csv
```

## Required columns (normalized contract)

```text
patent_id
applicant_city
applicant_province
applicant_address
geo_source
geo_match_confidence
geo_notes
```

Minimum raw-source columns from Chinese exports:

```text
公开公告号 / 公开号 / 申请公布号 / patent_id
申请人城市 / applicant_city
申请人省份 / applicant_province
申请人地址 / applicant_address
```

## Minimum acceptance (Atlas gate)

Measured **on the IIDS key list** after join by publication number:

- City fill rate >= 80%
- Province fill rate >= 80%
- Key match rate >= 95% (geography row for each filtered patent ID)
- >= 50 unique cities

## Preferred sources (in order)

1. CNIPA / Incopat / Patsnap / CNRDS / CSMAR keyed by publication number
2. Lens / Google Patents bulk export with applicant address fields
3. Applicant-address parsing from bibliographic records
4. Applicant-name registry matching (flag separately; lower confidence)

## After delivery

```powershell
make atlas-iids-geo-key-batches          # if batches not yet built
# place batch exports -> data/interim/iids_geo_exports/
make atlas-iids-geo-concat               # -> cnipa_patent_geography_2015_2024_raw.csv
make atlas-iids-geo-normalize            # -> cnipa_patent_geography_2015_2024.csv
make atlas-iids-geo-coverage-validate
make atlas-iids-geo-validate
make atlas-iids-geo
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json
```

Do not weaken `atlas_evidence_ready` gates.
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Write geography procurement brief from IIDS keys.")
    p.add_argument("--keys-csv", type=Path, default=None)
    p.add_argument("--output", type=Path, default=OUT_MD)
    args = p.parse_args()

    keys = args.keys_csv or FILTERED_PATENT_IDS_FOR_GEO_OUTPUT
    if not keys.exists():
        keys = PATENT_KEYS_FOR_GEO_OUTPUT
    if not keys.exists():
        print(f"ERROR: keys file not found: {keys}", file=sys.stderr)
        print("Run cloud full-convert and copy-back first.", file=sys.stderr)
        return 1

    brief = build_brief(keys)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(brief, encoding="utf-8")
    n, _, _ = _summarize_keys(keys)
    print(f"Wrote {args.output}")
    print(f"  patent IDs: {n:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
