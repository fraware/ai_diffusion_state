from diffusion_state.corporate_region_inference import infer_corporate_hq_from_applicant_name


def test_state_grid_province_anchor():
    geo = infer_corporate_hq_from_applicant_name("STATE GRID HUNAN ELECTRIC POWER CO LTD")
    assert geo is not None
    assert geo["applicant_city"] == "Changsha"


def test_cas_institute_explicit():
    geo = infer_corporate_hq_from_applicant_name("INST METAL RESEARCH CAS")
    assert geo is not None
    assert geo["applicant_city"] == "Shenyang"


def test_cas_default_beijing():
    geo = infer_corporate_hq_from_applicant_name("INST NOVEL PHYSICS CAS")
    assert geo is not None
    assert geo["applicant_city"] == "Beijing"
