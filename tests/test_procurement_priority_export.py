from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

from diffusion_state.procurement_priority_export import (
    load_unresolved_patent_ids,
    select_priority_applicants,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_GEO = ROOT / "tests/fixtures/iids_geography_sample.csv"


def test_load_unresolved_from_fixture() -> None:
    extra = Path(__file__).parent / "fixtures" / "geo_tiered_sample.csv"
    pd.DataFrame(
        [
            {
                "patent_id": "CN2018000001A",
                "applicant_city": "",
                "applicant_province": "",
                "applicant_address": "",
                "geo_source": "tiered",
                "geo_match_confidence": "unresolved",
                "geo_notes": "",
            },
            {
                "patent_id": "CN2018000002A",
                "applicant_city": "深圳市",
                "applicant_province": "广东省",
                "applicant_address": "addr",
                "geo_source": "tiered",
                "geo_match_confidence": "official_headquarters_page",
                "geo_notes": "",
            },
        ]
    ).to_csv(extra, index=False)
    ids = load_unresolved_patent_ids(extra)
    assert ids == {"CN2018000001A"}


def test_select_priority_applicants_cumulative() -> None:
    counts = Counter({"ACME": 500, "BETA": 300, "GAMMA": 100})
    selected = select_priority_applicants(counts, target_patents=600)
    assert "ACME" in selected
    assert "BETA" in selected
    assert selected["ACME"][0] == 1
