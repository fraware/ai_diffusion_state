from diffusion_state.tiered_geography_resolve import (
    UNRESOLVED_LABEL,
    resolve_tiered_geography,
)


def test_co_applicant_resolves_second():
    top_map = {
        "UNIV ZHEJIANG": {
            "applicant_city": "Hangzhou",
            "applicant_province": "Zhejiang",
            "geo_match_confidence": "university_location",
            "source_url": "https://example.edu",
            "notes": "test",
        }
    }
    geo, tier = resolve_tiered_geography(
        patent_id="CN2018123456A",
        applicant_name="UNKNOWN CORP LTD; UNIV ZHEJIANG",
        external={},
        top_map=top_map,
    )
    assert tier != UNRESOLVED_LABEL
    assert geo["applicant_city"] == "Hangzhou"
    assert "Co-applicant" in geo["geo_notes"]
