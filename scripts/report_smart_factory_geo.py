"""Print city-confidence summary for smart_factories_clean.csv."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT


def main() -> None:
    path = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    df = pd.read_csv(path)
    vc = df["city_confidence"].value_counts()
    known = df[df["city_confidence"].isin({"exact", "high", "medium"})]
    rate = len(known) / len(df)
    lines = [
        f"projects={len(df)}",
        "city_confidence:",
        vc.to_string(),
        f"exact+high+medium share={rate:.1%}",
    ]
    out = PROJECT_ROOT / "docs" / "smart_factory_geo_report.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
