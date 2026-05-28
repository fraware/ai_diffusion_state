from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_geography_batch import (
    concat_geography_batches,
    normalize_geography_batches,
    validate_all_export_batches,
)


def _write_keys(path: Path, ids: list[str]) -> None:
    pd.DataFrame(
        {
            "patent_id": ids,
            "publication_number": ids,
            "applicant_name": ["Firm"] * len(ids),
            "patent_title": ["T"] * len(ids),
            "application_year": ["2018"] * len(ids),
            "publication_year": ["2019"] * len(ids),
            "search_keyword": ["r"] * len(ids),
        }
    ).to_csv(path, index=False)


def _write_export(path: Path, rows: list[dict[str, str]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def test_batch_pipeline_concat_normalize_and_validate(tmp_path: Path) -> None:
    batch_dir = tmp_path / "keys"
    export_dir = tmp_path / "exports"
    batch_dir.mkdir()
    export_dir.mkdir()

    ids = [f"CN2018{i:04d}A" for i in range(10)]
    _write_keys(batch_dir / "iids_geo_keys_batch_001.csv", ids)
    _write_export(
        export_dir / "iids_geo_export_batch_001.csv",
        [
            {
                "patent_id": pid,
                "applicant_city": "苏州市",
                "applicant_province": "江苏省",
                "applicant_address": "addr",
                "geo_source": "cnipa_test",
                "geo_match_confidence": "exact_publication_number",
                "geo_notes": "",
            }
            for pid in ids
        ],
    )

    report = validate_all_export_batches(batch_dir, export_dir)
    assert report["all_passed"] is True

    raw = tmp_path / "raw.csv"
    n = concat_geography_batches(export_dir, raw)
    assert n == 10

    out = tmp_path / "cnipa_patent_geography_2015_2024.csv"
    stats = normalize_geography_batches(export_dir, out)
    assert stats["rows"] == 10
    assert stats["city_fill_rate"] == 1.0
    normalized = pd.read_csv(out)
    assert list(normalized.columns) == [
        "patent_id",
        "applicant_city",
        "applicant_province",
        "applicant_address",
        "geo_source",
        "geo_match_confidence",
        "geo_notes",
    ]
