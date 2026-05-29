from pathlib import Path

from diffusion_state.iids_geo_stream import load_geography_lookup_dict


def test_geography_lookup_has_cities(tmp_path: Path) -> None:
    geo = tmp_path / "geo.csv"
    geo.write_text(
        "patent_id,applicant_city,applicant_province,applicant_address,geo_source,geo_match_confidence,geo_notes\n"
        "CN20180001A,Shenzhen,Guangdong,addr,test,official_headquarters_page,\n",
        encoding="utf-8",
    )
    lookup = load_geography_lookup_dict(geo)
    assert lookup["CN20180001A"][0] == "Shenzhen"
