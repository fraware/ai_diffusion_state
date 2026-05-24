from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.iids_geo_join import build_geography_from_export
from diffusion_state.utils import PROJECT_ROOT

FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


def test_build_geography_from_cnipa_export(tmp_path: Path) -> None:
    export = tmp_path / "cnipa_sample.csv"
    pd.read_csv(FIXTURES / "patents_cnipa_micro.csv", nrows=20).to_csv(export, index=False, encoding="utf-8-sig")
    rows = build_geography_from_export(export, iids_csv=None, source_label="cnipa_test")
    assert len(rows) == 20
    assert rows["applicant_city"].astype(str).str.len().gt(0).any()
