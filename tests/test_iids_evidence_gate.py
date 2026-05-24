from __future__ import annotations

import pandas as pd

from diffusion_state.validate_no_fixture_patents import _detect_fixture_signals


def test_iids_abstract_equals_claims_not_fixture_signal() -> None:
    df = pd.DataFrame(
        {
            "patent_id": [f"CN201812345{i}A" for i in range(10)],
            "applicant_name": ["Acme Co"] * 10,
            "patent_title": ["Robot controller"] * 10,
            "abstract": ["Abstract text"] * 10,
            "claims_or_description": ["Abstract text"] * 10,
            "applicant_city": ["苏州市"] * 10,
            "source": ["opendatalab_iids"] * 10,
            "source_url_or_file": ["Gracie/IIDS"] * 10,
        }
    )
    signals = _detect_fixture_signals(df)
    assert signals["abstract_equals_claims"] is False
    assert signals["geography_ready"] is True
    assert signals["iids_source_share"] == 1.0


def test_iids_without_geography_not_ready() -> None:
    df = pd.DataFrame(
        {
            "patent_id": ["CN2018123456A"],
            "applicant_name": ["Acme Co"],
            "patent_title": ["Robot controller"],
            "abstract": ["Abstract text"],
            "claims_or_description": ["Abstract text"],
            "applicant_city": [""],
            "source": ["opendatalab_iids"],
            "source_url_or_file": ["Gracie/IIDS"],
        }
    )
    signals = _detect_fixture_signals(df)
    assert signals["geography_ready"] is False
    assert signals["abstract_equals_claims"] is False
