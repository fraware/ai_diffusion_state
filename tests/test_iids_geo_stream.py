from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_geo_stream import (
    join_patent_geography_streaming,
    measure_geography_key_coverage,
)


def test_key_coverage_on_sample(tmp_path: Path) -> None:
    keys = tmp_path / "keys.csv"
    geo = tmp_path / "geo.csv"
    ids = [f"CN2018{i:04d}A" for i in range(5)]
    pd.DataFrame(
        {"patent_id": ids, "publication_number": ids, "application_year": ["2018"] * 5}
    ).to_csv(keys, index=False)
    pd.DataFrame(
        {
            "patent_id": ids,
            "applicant_city": ["苏州市", "杭州市", "深圳市", "北京市", ""],
            "applicant_province": ["江苏省", "浙江省", "广东省", "北京市", ""],
            "applicant_address": ["a"] * 5,
            "geo_source": ["test"] * 5,
            "geo_match_confidence": ["exact_publication_number"] * 5,
            "geo_notes": [""] * 5,
        }
    ).to_csv(geo, index=False)
    stats = measure_geography_key_coverage(geo, keys)
    assert stats["n_keys"] == 5
    assert stats["city_fill_rate"] == 0.8
    assert stats["province_fill_rate"] == 0.8
    assert stats["key_match_rate"] == 1.0


def test_streaming_join_fills_address_fields(tmp_path: Path) -> None:
    iids = tmp_path / "iids.csv"
    geo = tmp_path / "geo.csv"
    out = tmp_path / "out.csv"
    pd.DataFrame(
        {
            "patent_id": ["CN2018123456A"],
            "applicant_name": ["Acme"],
            "applicant_city": [""],
            "applicant_province": [""],
            "applicant_address": [""],
            "patent_title": ["Robot"],
            "application_year": ["2018"],
            "publication_year": ["2019"],
            "search_keyword": ["robot"],
            "source": ["opendatalab_iids"],
        }
    ).to_csv(iids, index=False)
    pd.DataFrame(
        {
            "patent_id": ["CN2018123456A"],
            "applicant_city": ["苏州市"],
            "applicant_province": ["江苏省"],
            "applicant_address": ["江苏省苏州市"],
            "geo_source": ["cnipa_test"],
            "geo_match_confidence": ["exact_publication_number"],
            "geo_notes": [""],
        }
    ).to_csv(geo, index=False)
    stats = join_patent_geography_streaming(iids, geo, out)
    merged = pd.read_csv(out)
    assert merged.loc[0, "applicant_city"] == "苏州市"
    assert stats["city_fill_rate"] == 1.0
