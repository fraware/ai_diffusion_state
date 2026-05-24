from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_copyback import MIN_IIDS_ROWS, verify_copyback_artifacts
from diffusion_state.iids_paths import (
    DEFAULT_IIDS_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
    PATENT_KEYS_FOR_GEO_OUTPUT,
)
from diffusion_state.iids_patent_keys import KEY_COLUMNS, export_patent_keys_for_geography


def test_verify_copyback_passes_with_synthetic_artifacts(tmp_path: Path, monkeypatch) -> None:
    raw = tmp_path / "patents"
    raw.mkdir()
    tables = tmp_path / "tables"
    tables.mkdir()

    iids = raw / DEFAULT_IIDS_OUTPUT.name
    rows = MIN_IIDS_ROWS + 10
    pd.DataFrame(
        {
            "patent_id": [f"CN2018{i:06d}A" for i in range(rows)],
            "applicant_name": ["Acme"] * rows,
            "patent_title": ["Robot"] * rows,
            "application_year": ["2018"] * rows,
            "publication_year": ["2019"] * rows,
            "search_keyword": ["robotics"] * rows,
            "applicant_city": [""] * rows,
            "abstract": ["a"] * rows,
            "claims_or_description": ["a"] * rows,
            "ipc_or_cpc": ["B25J"] * rows,
            "patent_type": ["发明"] * rows,
            "source": ["opendatalab_iids"] * rows,
            "source_url_or_file": ["Gracie/IIDS"] * rows,
        }
    ).to_csv(iids, index=False)

    keys_out = tables / "table_P9.csv"
    export_patent_keys_for_geography(iids, keys_out, alias_csv=raw / FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.name)
    pd.DataFrame([{"source_file": iids.name, "export_owner": "test"}]).to_csv(
        raw / "patent_source_manifest_draft.csv", index=False
    )
    (tables / "table_P0.csv").write_text("ok\n", encoding="utf-8")

    monkeypatch.setattr("diffusion_state.iids_copyback.DEFAULT_IIDS_OUTPUT", iids)
    monkeypatch.setattr("diffusion_state.iids_copyback.PATENT_KEYS_FOR_GEO_OUTPUT", keys_out)
    monkeypatch.setattr(
        "diffusion_state.iids_copyback.FILTERED_PATENT_IDS_FOR_GEO_OUTPUT",
        raw / FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.name,
    )
    monkeypatch.setattr("diffusion_state.iids_copyback.MANIFEST_DRAFT", raw / "patent_source_manifest_draft.csv")
    monkeypatch.setattr("diffusion_state.iids_copyback.P0_DIAG", tables / "table_P0.csv")
    monkeypatch.setattr("diffusion_state.iids_copyback.discover_geography_supplement", lambda: None)

    report = verify_copyback_artifacts()
    assert report.ready_for_geography_procurement
    assert not report.blockers
    assert report.unique_patent_ids >= MIN_IIDS_ROWS
