from diffusion_state.university_region_inference import infer_university_hq_from_applicant_name


def test_univ_henan_anchor():
    geo = infer_university_hq_from_applicant_name("UNIV HENAN")
    assert geo is not None
    assert geo["applicant_city"] == "Zhengzhou"
    assert geo["geo_match_confidence"] == "university_location"


def test_univ_ambiguous_multi_region():
    assert infer_university_hq_from_applicant_name("UNIV HENAN HUBEI") is None


def test_non_univ():
    assert infer_university_hq_from_applicant_name("HUAWEI TECH CO LTD") is None


def test_uestc_alias():
    geo = infer_university_hq_from_applicant_name("UNIV ELECTRONIC SCIENCE & TECH CHINA")
    assert geo is not None
    assert geo["applicant_city"] == "Chengdu"
