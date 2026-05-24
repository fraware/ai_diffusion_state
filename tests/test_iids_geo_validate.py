from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_geo_join import (
    MINIMUM_ACCEPTANCE,
    evaluate_geography_acceptance,
    validate_geography_supplement,
)


def test_geography_minimum_acceptance_passes_on_rich_sample(tmp_path: Path) -> None:
    geo = tmp_path / "cnipa_patent_geography_2015_2024.csv"
    rows = []
    cities = [f"City{i}" for i in range(55)]
    for i in range(600):
        rows.append(
            {
                "patent_id": f"CN2018{i:06d}A",
                "publication_number": f"CN2018{i:06d}A",
                "applicant_name": f"Firm{i}",
                "applicant_city": cities[i % len(cities)],
                "applicant_province": "江苏省",
                "applicant_address": f"{cities[i % len(cities)]} address",
                "geography_source": "cnipa_test",
                "geography_source_url": "https://example.test/geo",
                "city_mapping_confidence": "high",
                "notes": "",
            }
        )
    pd.DataFrame(rows).to_csv(geo, index=False)
    stats, _ = validate_geography_supplement(geo)
    ok, issues = evaluate_geography_acceptance(stats, thresholds=MINIMUM_ACCEPTANCE, label="minimum")
    assert ok, issues
