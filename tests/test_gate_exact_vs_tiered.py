from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_geography_gate import collect_iids_geography_gate


def test_tiered_fill_does_not_set_exact_ready(tmp_path: Path, monkeypatch) -> None:
    """65% tiered geography must not pass iids_geography_ready or evidence chain."""
    iids = tmp_path / "iids.csv"
    keys = tmp_path / "keys.csv"
    geo = tmp_path / "geo.csv"

    n = 100
    ids = [f"CN2018{i:04d}A" for i in range(n)]
    pd.DataFrame(
        {
            "patent_id": ids,
            "publication_number": ids,
            "applicant_name": ["Firm"] * n,
            "patent_title": ["T"] * n,
            "application_year": ["2018"] * n,
            "publication_year": ["2019"] * n,
            "search_keyword": ["ai"] * n,
        }
    ).to_csv(iids, index=False)
    pd.DataFrame(
        {
            "patent_id": ids,
            "publication_number": ids,
            "applicant_name": ["Firm"] * n,
            "patent_title": ["T"] * n,
            "application_year": ["2018"] * n,
            "publication_year": ["2019"] * n,
            "search_keyword": ["ai"] * n,
        }
    ).to_csv(keys, index=False)

    rows = []
    for i, pid in enumerate(ids):
        if i < 65:
            rows.append(
                {
                    "patent_id": pid,
                    "applicant_city": "杭州市",
                    "applicant_province": "浙江省",
                    "applicant_address": "addr",
                    "geo_source": "tiered",
                    "geo_match_confidence": "official_headquarters_page",
                    "geo_notes": "",
                }
            )
        else:
            rows.append(
                {
                    "patent_id": pid,
                    "applicant_city": "",
                    "applicant_province": "",
                    "applicant_address": "",
                    "geo_source": "tiered",
                    "geo_match_confidence": "unresolved",
                    "geo_notes": "",
                }
            )
    pd.DataFrame(rows).to_csv(geo, index=False)

    import diffusion_state.iids_geography_gate as gate_mod

    monkeypatch.setattr(gate_mod, "is_real_export_filename", lambda _n: True)

    g = collect_iids_geography_gate(
        iids_csv=iids,
        keys_csv=keys,
        geography_csv=geo,
        min_city_fill=0.8,
    )
    assert g["tiered_robustness_ready"] is True
    assert g["exact_geography_ready"] is False
    assert g["iids_geography_ready"] is False
    assert g["ready_for_evidence_chain"] is False
