from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from diffusion_state.atlas_status import collect_atlas_status
from diffusion_state.iids_geography_gate import collect_iids_geography_gate
from diffusion_state.iids_patent_keys import KEY_COLUMNS, export_patent_keys_for_geography


def _write_iids(path: Path, n: int = 3) -> None:
    rows = [
        {
            "patent_id": f"CN2018{i:04d}A",
            "applicant_name": f"Firm{i}",
            "patent_title": f"Title{i}",
            "application_year": "2018",
            "publication_year": "2019",
            "search_keyword": "robot",
            "source": "opendatalab_iids",
        }
        for i in range(n)
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


def _write_keys(path: Path, patent_ids: list[str]) -> None:
    pd.DataFrame(
        {
            "patent_id": patent_ids,
            "publication_number": patent_ids,
            "applicant_name": ["Firm"] * len(patent_ids),
            "patent_title": ["Title"] * len(patent_ids),
            "application_year": ["2018"] * len(patent_ids),
            "publication_year": ["2019"] * len(patent_ids),
            "search_keyword": ["robot"] * len(patent_ids),
        }
    ).to_csv(path, index=False)


def _write_geography(path: Path, patent_ids: list[str], *, city: str = "杭州市") -> None:
    pd.DataFrame(
        {
            "patent_id": patent_ids,
            "applicant_city": [city] * len(patent_ids),
            "applicant_province": ["浙江省"] * len(patent_ids),
            "applicant_address": ["addr"] * len(patent_ids),
            "geo_source": ["cnipa_test"] * len(patent_ids),
            "geo_match_confidence": ["exact_publication_number"] * len(patent_ids),
            "geo_notes": [""] * len(patent_ids),
        }
    ).to_csv(path, index=False)


def test_geography_gate_blocks_evidence_when_geo_missing(tmp_path: Path) -> None:
    iids = tmp_path / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
    keys = tmp_path / "iids_filtered_patent_ids_for_geography.csv"
    geo = tmp_path / "cnipa_patent_geography_2015_2024.csv"
    _write_iids(iids)
    _write_keys(keys, ["CN20180000A", "CN20180001A", "CN20180002A"])

    gate = collect_iids_geography_gate(iids_csv=iids, keys_csv=keys, geography_csv=geo)
    assert gate["iids_patent_export_ready"] is True
    assert gate["iids_geography_ready"] is False
    assert gate["ready_for_evidence_chain"] is False


def test_geography_gate_passes_with_fill(tmp_path: Path) -> None:
    iids = tmp_path / "opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"
    keys = tmp_path / "iids_filtered_patent_ids_for_geography.csv"
    geo = tmp_path / "cnipa_patent_geography_2015_2024.csv"
    ids = [f"CN2018{i:04d}A" for i in range(10)]
    _write_iids(iids, n=10)
    _write_keys(keys, ids)
    _write_geography(geo, ids)

    gate = collect_iids_geography_gate(iids_csv=iids, keys_csv=keys, geography_csv=geo)
    assert gate["iids_geography_ready"] is True
    assert gate["ready_for_evidence_chain"] is True
    assert gate["geography_city_fill_rate"] >= 0.8


def test_atlas_status_blocks_evidence_without_geography(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "diffusion_state.atlas_status.write_evidence_gate_report",
        lambda: {
            "fixture_patents_detected": False,
            "real_patent_source_present": True,
            "patent_source_status": "real_multi_source",
        },
    )
    monkeypatch.setattr(
        "diffusion_state.atlas_status.collect_iids_geography_gate",
        lambda: {
            "iids_patent_export_ready": True,
            "iids_geography_ready": False,
            "ready_for_geography_procurement": True,
            "ready_for_evidence_chain": False,
            "recommended_next": "build data/raw/patents/cnipa_patent_geography_2015_2024.csv",
        },
    )
    status = collect_atlas_status()
    assert status["atlas_evidence_ready"] is False
    assert status["atlas_ready"] is False
    assert status["ready_for_evidence_chain"] is False
    assert status["iids_geography_ready"] is False
    assert status["atlas_models_ready"] is False


def test_atlas_status_allows_evidence_with_geography(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "diffusion_state.atlas_status.write_evidence_gate_report",
        lambda: {
            "fixture_patents_detected": False,
            "real_patent_source_present": True,
            "patent_source_status": "real_multi_source",
        },
    )
    monkeypatch.setattr(
        "diffusion_state.atlas_status.collect_iids_geography_gate",
        lambda: {
            "iids_patent_export_ready": True,
            "iids_geography_ready": True,
            "ready_for_geography_procurement": True,
            "ready_for_evidence_chain": True,
            "recommended_next": "make atlas-iids-control-evidence-chain",
        },
    )
    status = collect_atlas_status()
    assert status["iids_geography_ready"] is True
    assert status["ready_for_evidence_chain"] is True


def test_patent_keys_header_exact(tmp_path: Path) -> None:
    iids = tmp_path / "iids.csv"
    out = tmp_path / "keys.csv"
    pd.DataFrame(
        {
            "patent_id": ["CN2018123456A"],
            "applicant_name": ["Acme"],
            "patent_title": ["Robot"],
            "application_year": ["2018"],
            "publication_year": ["2019"],
            "search_keyword": ["robotics"],
        }
    ).to_csv(iids, index=False)
    export_patent_keys_for_geography(iids, out, alias_csv=None)
    header = out.read_text(encoding="utf-8-sig").splitlines()[0]
    assert header == ",".join(KEY_COLUMNS)


def test_patent_keys_streaming_no_pandas_full_load(tmp_path: Path) -> None:
    import diffusion_state.iids_patent_keys as mod

    assert "pd.read_csv" not in Path(mod.__file__).read_text(encoding="utf-8")
