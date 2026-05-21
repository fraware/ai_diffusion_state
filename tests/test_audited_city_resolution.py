from __future__ import annotations

from diffusion_state.audited_city_resolution import infer_audited_resolution
from diffusion_state.smart_factory_geo import resolve_geo


def test_infer_ningde_from_firm_token():
    res = infer_audited_resolution(
        location_raw="福建省",
        firm_name_zh="宁德新能源科技有限公司",
        project_name_zh="电池智能工厂",
        province="Fujian",
        source_url="https://example.com/list",
    )
    assert res is not None
    assert res.city == "Ningde"
    assert res.evidence_type == "firm_embedded_city_token"


def test_registry_match_dahua():
    res = infer_audited_resolution(
        location_raw="浙江省",
        firm_name_zh="浙江大华技术股份有限公司",
        project_name_zh="视觉物联产品智能工厂",
        province="Zhejiang",
        source_url="https://example.com/list",
    )
    assert res is not None
    assert res.city == "Hangzhou"


def test_resolve_geo_uses_audited_for_province_only():
    geo = resolve_geo("安徽省", "奇瑞新能源汽车股份有限公司", "新型结构电动车智能工厂")
    assert geo.city == "Wuhu"
    assert geo.city_confidence == "high"


def test_parenthetical_huaian_in_firm_name():
    res = infer_audited_resolution(
        location_raw="江苏",
        firm_name_zh="庆鼎精密电子（淮安）有限公司",
        project_name_zh="PCB智能工厂",
        province="Jiangsu",
        source_url="https://example.com/list",
    )
    assert res is not None
    assert res.city == "Huai'an"


def test_jiujiang_branch_in_project_name():
    res = infer_audited_resolution(
        location_raw="江西省",
        firm_name_zh="中国石油化工股份有限公司",
        project_name_zh="九江分公司石化智能工厂",
        province="Jiangxi",
        source_url="https://example.com/list",
    )
    assert res is not None
    assert res.city == "Jiujiang"
