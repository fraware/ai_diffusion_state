from pathlib import Path

from diffusion_state.iids_geo_stream import join_patent_geography_streaming


def test_inplace_join_preserves_row_count(tmp_path: Path) -> None:
    iids = tmp_path / "iids.csv"
    geo = tmp_path / "geo.csv"
    iids.write_text(
        "patent_id,applicant_name,applicant_city,applicant_province,applicant_address\n"
        "CN20180001A,ACME,,,\n"
        "CN20180002A,BETA,,,\n",
        encoding="utf-8",
    )
    geo.write_text(
        "patent_id,applicant_city,applicant_province,applicant_address,geo_source,geo_match_confidence,geo_notes\n"
        "CN20180001A,Shenzhen,Guangdong,addr,test,applicant_name_city_token,\n",
        encoding="utf-8",
    )
    stats = join_patent_geography_streaming(iids, geo, iids)
    assert stats["rows"] == 2
    assert stats["city_fill_rate"] == 0.5
    lines = iids.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
