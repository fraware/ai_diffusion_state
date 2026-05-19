from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_smart_factory_sample_columns():
    df = pd.read_csv(ROOT / "data" / "seed" / "smart_factory_sample.csv")
    required = {"batch", "firm", "project", "province_or_city", "source_url"}
    assert required.issubset(df.columns)
