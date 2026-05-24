"""Generate a geography procurement brief from filtered IIDS patent keys."""
from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.iids_paths import FILTERED_PATENT_IDS_FOR_GEO_OUTPUT, PATENT_KEYS_FOR_GEO_OUTPUT  # noqa: E402

OUT_MD = ROOT / "docs" / "ATLAS_IIDS_GEOGRAPHY_PROCUREMENT_BRIEF.md"


def build_brief(keys_csv: Path) -> str:
    df = pd.read_csv(keys_csv, low_memory=False)
    n = len(df)
    years = (
        pd.to_numeric(df.get("application_year", pd.Series(dtype=float)), errors="coerce")
        .dropna()
        .astype(int)
    )
    year_min = int(years.min()) if not years.empty else ""
    year_max = int(years.max()) if not years.empty else ""
    ts = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")

    return f"""# Atlas IIDS geography procurement brief

Generated: {ts}

Source keys file: `{keys_csv.relative_to(ROOT).as_posix()}`

## Request

Export **address metadata only** for the patent IDs in the keys file. Do not download a full patent universe.

| Metric | Value |
|--------|-------|
| Unique patent IDs | {n:,} |
| Application years | {year_min}–{year_max} |

## Required output file

Place on the control laptop:

```text
data/raw/patents/cnipa_patent_geography_2015_2024.csv
```

## Required columns

```text
patent_id
publication_number
applicant_name
applicant_city
applicant_province
applicant_address
geography_source
geography_source_url
city_mapping_confidence
notes
```

## Minimum acceptance (Atlas gate)

- City fill rate >= 80%
- >= 50 unique cities
- >= 500 retained industrial-AI records after join with IIDS export

## Acceptable sources

- CNIPA export (publication number + applicant address)
- Lens export (publication number + applicant address/city)
- CNKI / CNRDS / CSMAR patent metadata with address fields

## After delivery

```powershell
make atlas-iids-geo-build
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
    print(f"Wrote {args.output}")
    print(f"  patent IDs: {pd.read_csv(keys).shape[0]:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
