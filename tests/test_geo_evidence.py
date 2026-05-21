from __future__ import annotations

from diffusion_state.geo_evidence import (
    classify_resolution_class,
    evidence_url_for_class,
    is_external_evidence_url,
    normalize_evidence_type,
)


def test_registry_annual_report_with_list_url_is_rule_based():
    source = "https://cn.solarbe.com/news/20250103/92225.html"
    et = normalize_evidence_type("company_annual_report", source, source)
    assert et == "firm_registry_match"
    assert classify_resolution_class(et, source, source) == "rule_based_text_inference"


def test_miit_location_is_official():
    source = "https://cn.solarbe.com/news/20250103/92225.html"
    assert classify_resolution_class("miit_location_field", source, source) == "official_location_exact"


def test_external_url_when_not_list_page():
    source = "https://cn.solarbe.com/news/20250103/92225.html"
    external = "https://www.example.com/annual-report-2024"
    assert is_external_evidence_url(external, source)
    rc = classify_resolution_class("company_annual_report", external, source)
    assert rc == "external_evidence_verified"
    assert evidence_url_for_class(rc, source, source, external_url=external) == external
