from diffusion_state.applicant_exact_aliases import geography_from_exact_alias


def test_sun_yat_sen():
    geo = geography_from_exact_alias("SUN YAT-SEN UNIV")
    assert geo is not None
    assert geo["applicant_city"] == "Guangzhou"


def test_changan_apostrophe():
    geo = geography_from_exact_alias("CHANG'AN UNIV")
    assert geo is not None
    assert geo["applicant_city"] == "Xi'an"
