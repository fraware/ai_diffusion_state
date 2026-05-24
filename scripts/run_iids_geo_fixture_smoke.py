"""CI smoke: validate and join fixture geography to smoke IIDS output."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_GEO = ROOT / "tests" / "fixtures" / "iids_geography_sample.csv"
SMOKE_IIDS = ROOT / "outputs" / "smoke" / "iids" / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
SMOKE_GEO = ROOT / "outputs" / "smoke" / "iids" / "cnipa_patent_geography_2015_2024.csv"
PYTHON = sys.executable


def _run(cmd: list[str]) -> int:
    print(" ".join(cmd))
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def _ensure_smoke_iids() -> int:
    if SMOKE_IIDS.exists():
        return 0
    return _run(
        [
            PYTHON,
            "scripts/64_run_atlas_iids_pipeline.py",
            "--detail-sql",
            "tests/fixtures/iids_base_patent_detail_sample.sql",
            "--law-status-sql",
            "tests/fixtures/iids_base_patent_law_status_sample.sql",
            "--smoke-rows",
            "5000",
            "--skip-geo",
        ]
    )


def _build_fixture_geo() -> None:
    raw = pd.read_csv(FIXTURE_GEO)
    out = pd.DataFrame(
        {
            "patent_id": raw["patent_id"].astype(str).str.strip(),
            "publication_number": raw["publication_number"].astype(str).str.strip(),
            "applicant_name": "fixture applicant",
            "applicant_city": raw["applicant_city"].astype(str).str.strip(),
            "applicant_province": raw["applicant_province"].astype(str).str.strip(),
            "applicant_address": raw["applicant_address"].astype(str).str.strip(),
            "geography_source": "fixture",
            "geography_source_url": "tests/fixtures/iids_geography_sample.csv",
            "city_mapping_confidence": "high",
            "notes": "CI fixture only",
        }
    )
    SMOKE_GEO.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(SMOKE_GEO, index=False, encoding="utf-8-sig")


def main() -> int:
    code = _ensure_smoke_iids()
    if code != 0:
        return code
    _build_fixture_geo()
    code = _run(
        [PYTHON, "scripts/63_validate_patent_geography_supplement.py", "--geo-csv", str(SMOKE_GEO), "--fixture-smoke"]
    )
    if code != 0:
        return code
    return _run(
        [
            PYTHON,
            "scripts/62_join_iids_patent_geography.py",
            "--iids-csv",
            str(SMOKE_IIDS),
            "--geo-csv",
            str(SMOKE_GEO),
            "--fixture-smoke",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
