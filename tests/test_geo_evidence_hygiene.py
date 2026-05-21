from __future__ import annotations

import pandas as pd

from diffusion_state.geo_evidence import validate_evidence_hygiene


def test_validate_catches_external_class_with_list_url_only():
    df = pd.DataFrame(
        [
            {
                "project_id": "x",
                "resolution_class": "external_evidence_verified",
                "evidence_type": "company_annual_report",
                "evidence_url": "https://cn.solarbe.com/news/20250103/92225.html",
                "external_evidence_url": "",
            }
        ]
    )
    errs = validate_evidence_hygiene(df)
    assert errs


def test_validate_ok_for_rule_based_registry():
    df = pd.DataFrame(
        [
            {
                "project_id": "x",
                "resolution_class": "rule_based_text_inference",
                "evidence_type": "firm_registry_match",
                "evidence_url": "https://cn.solarbe.com/news/20250103/92225.html",
            }
        ]
    )
    assert validate_evidence_hygiene(df) == []
