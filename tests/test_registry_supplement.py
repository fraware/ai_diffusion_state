from __future__ import annotations

from diffusion_state.audited_city_resolution import _load_firm_registry, infer_audited_resolution


def test_supplement_registry_loads():
    entries = _load_firm_registry()
    assert len(entries) >= 60


def test_supplement_resolves_weifang_firm():
    res = infer_audited_resolution(
        location_raw="山东省",
        firm_name_zh="潍柴动力股份有限公司",
        project_name_zh="发动机智能工厂",
        province="Shandong",
        source_url="https://example.com/list",
    )
    assert res is not None
    assert res.city == "Weifang"
