from __future__ import annotations

import pandas as pd

from diffusion_state.iids_patent_keys import export_patent_keys_for_geography


def test_export_patent_keys_deduplicates_and_maps_publication_number(tmp_path) -> None:
    iids = tmp_path / "iids.csv"
    out = tmp_path / "keys.csv"
    pd.DataFrame(
        {
            "patent_id": ["CN2018123456A", "CN2018123456A", "CN2019123456B"],
            "applicant_name": ["Acme", "Acme", "Beta"],
            "application_year": ["2018", "2018", "2019"],
            "publication_year": ["2019", "2019", "2020"],
            "search_keyword": ["robotics", "robotics", "vision"],
        }
    ).to_csv(iids, index=False)

    stats = export_patent_keys_for_geography(iids, out)
    assert stats.unique_patent_ids == 2
    keys = pd.read_csv(out)
    assert list(keys.columns) == [
        "patent_id",
        "publication_number",
        "applicant_name",
        "application_year",
        "publication_year",
        "search_keyword",
    ]
    assert keys["publication_number"].tolist() == keys["patent_id"].tolist()
