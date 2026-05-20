from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from diffusion_state.build_paper_bundle import build_paper_bundle
from diffusion_state.smart_factory_overrides import apply_city_overrides

ROOT = Path(__file__).resolve().parents[1]


def test_apply_city_override_updates_row():
    base = pd.DataFrame(
        [
            {
                "project_id": "2024_test_0001",
                "city": "unknown",
                "province": "Fujian",
                "city_confidence": "unknown",
                "manual_override_flag": 0,
                "parse_method": "html_table",
                "notes": "province-only",
            }
        ]
    )
    overrides = pd.DataFrame(
        [
            {
                "project_id": "2024_test_0001",
                "city": "Jinjiang",
                "province": "Fujian",
                "city_confidence": "high",
                "override_source": "firm_registry_2024",
                "notes": "City from audited registry entry cited in source note.",
            }
        ]
    )
    out = apply_city_overrides(base, overrides)
    row = out.iloc[0]
    assert row["city"] == "Jinjiang"
    assert row["manual_override_flag"] == 1
    assert row["parse_method"] == "manual_override"
    assert "manual override" in row["notes"]


@pytest.mark.skipif(
    not (ROOT / "outputs/tables/table_1_dataset_summary.csv").exists(),
    reason="Run make analysis first",
)
def test_build_paper_bundle_strict():
    manifest = build_paper_bundle(strict=True)
    assert not manifest["missing_required"]
    assert (ROOT / "paper/artifact_manifest.json").exists()
    assert (ROOT / "paper/claim_table_map.csv").exists()
