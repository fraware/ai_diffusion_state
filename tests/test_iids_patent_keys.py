from __future__ import annotations

import pandas as pd

from diffusion_state.iids_patent_keys import KEY_COLUMNS, export_patent_keys_for_geography


def test_export_patent_keys_deduplicates_and_maps_publication_number(tmp_path) -> None:
    iids = tmp_path / "iids.csv"
    out = tmp_path / "keys.csv"
    alias = tmp_path / "alias.csv"
    pd.DataFrame(
        {
            "patent_id": ["CN2018123456A", "CN2018123456A", "CN2019123456B"],
            "applicant_name": ["Acme", "Acme", "Beta"],
            "patent_title": ["Robot arm", "Robot arm", "Vision system"],
            "application_year": ["2018", "2018", "2019"],
            "publication_year": ["2019", "2019", "2020"],
            "search_keyword": ["robotics", "robotics", "vision"],
        }
    ).to_csv(iids, index=False)

    stats = export_patent_keys_for_geography(iids, out, alias_csv=alias)
    assert stats.unique_patent_ids == 2
    keys = pd.read_csv(out)
    assert list(keys.columns) == list(KEY_COLUMNS)
    assert keys["publication_number"].tolist() == keys["patent_id"].tolist()
    assert keys.loc[keys["patent_id"] == "CN2018123456A", "patent_title"].iloc[0] == "Robot arm"
    assert alias.exists()
    assert pd.read_csv(alias).shape[0] == 2
