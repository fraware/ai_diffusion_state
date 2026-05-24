from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_merge_module():
    spec = importlib.util.spec_from_file_location(
        "merge_manifest_mod",
        ROOT / "scripts" / "68_merge_patent_manifest_draft.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "src"))
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_merge_manifest_warn_only_returns_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_merge_module()
    raw = tmp_path / "patents"
    raw.mkdir()
    draft = raw / "patent_source_manifest_draft.csv"
    manifest = raw / "patent_source_manifest.csv"

    pd.DataFrame(
        {
            "source_file": ["opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv"],
            "data_provider": ["OpenXLab IIDS"],
            "proprietary_or_public": ["FILL_ME"],
            "export_owner": ["FILL_ME"],
            "record_count": [1000],
        }
    ).to_csv(draft, index=False)

    monkeypatch.setattr(mod, "DRAFT", draft)
    monkeypatch.setattr(mod, "MANIFEST_PATH", manifest)
    monkeypatch.setattr(mod, "validate_patent_source_manifest", lambda: ["FILL_ME remaining"])

    assert mod.merge_manifest(warn_only=True) == 0
    assert manifest.exists()
