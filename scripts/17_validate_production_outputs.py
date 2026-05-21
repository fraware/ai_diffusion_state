"""Fail if paper-facing artifacts reference CI stub controls or stale sprint numbers."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.panel_controls import STUB_SOURCE_MARKERS, city_controls_source
from diffusion_state.utils import PROJECT_ROOT

PAPER_PATHS = [
    PROJECT_ROOT / "paper" / "results_memo.md",
    PROJECT_ROOT / "paper" / "red_team_memo.md",
    PROJECT_ROOT / "paper" / "reviewer_results_snapshot.md",
    PROJECT_ROOT / "paper" / "claim_table_map.csv",
    PROJECT_ROOT / "paper" / "data_appendix.md",
]

MAIN_TABLES = PROJECT_ROOT / "paper" / "main_tables"

STUB_PHRASES = (
    "pipeline_ci_stub_not_for_paper",
    "city-controls-stub",
    "stub Model",
    "synthetic controls",
    "make city-controls-stub",
)

STALE_NUMERIC_PHRASES = (
    "125 cities, 382",
    "125-city",
    "382 listed projects",
    "coef ≈ 2.04 vs. 3.92",
    "coef ≈ 2.04 vs 3.92",
    "mean 8.33 vs 2.83",
    "8.33 vs 2.83",
    "≥250 resolved",
    ">=250 resolved",
    "Audited override rows",
    "audited override rows",
    "audited overrides",
)

ALLOW_STUB_CONTEXT = (
    "CI only",
    "CI stub",
    "not for paper",
    "do not cite",
    "no stub",
    "no synthetic",
    "not used",
    "disabled",
    "BLOCKED",
    "blocked until",
    "never used",
    "excluded",
)


def _line_allowed_stub(line: str) -> bool:
    low = line.lower()
    return any(tok.lower() in low for tok in ALLOW_STUB_CONTEXT)


def main() -> int:
    import os

    errors: list[str] = []

    src = city_controls_source()
    if src == "stub":
        errors.append(
            "data/processed/city_controls_year.csv uses CI stub — run make purge-stub-controls "
            "then make city-controls with EPS/NBS"
        )

    for path in PAPER_PATHS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in STUB_PHRASES:
            if phrase in text:
                for i, line in enumerate(text.splitlines(), 1):
                    if phrase in line and not _line_allowed_stub(line):
                        errors.append(f"{path.relative_to(ROOT)}:{i}: stub phrase '{phrase}'")
        for phrase in STALE_NUMERIC_PHRASES:
            if phrase.lower() in text.lower():
                for i, line in enumerate(text.splitlines(), 1):
                    if phrase.lower() in line.lower():
                        errors.append(f"{path.relative_to(ROOT)}:{i}: stale phrase '{phrase}'")

    t5 = PROJECT_ROOT / "outputs" / "tables" / "table_5_controlled_adoption_models.csv"
    if t5.exists() and src != "production":
        t5df = pd.read_csv(t5)
        if not (t5df["term"] == "skipped").all():
            errors.append(
                "table_5 has estimated coefficients without production controls — rerun make analysis"
            )

    if MAIN_TABLES.exists():
        for csv in MAIN_TABLES.glob("*.csv"):
            df = pd.read_csv(csv)
            blob = df.to_csv(index=False)
            for phrase in STUB_PHRASES:
                if phrase in blob:
                    errors.append(f"{csv.relative_to(ROOT)}: contains '{phrase}'")

    processed = PROJECT_ROOT / "data" / "processed" / "city_controls_year.csv"
    if processed.exists():
        df = pd.read_csv(processed)
        if "source_name" in df.columns:
            bad = df["source_name"].astype(str).str.contains(STUB_SOURCE_MARKERS[0], case=False, na=False)
            if bad.any() and src == "production":
                errors.append("city_controls_year.csv: stub source_name flagged as production")

    if errors:
        print("FAIL production-check:")
        for e in errors:
            print(f"  {e}")
        return 1

    print("OK production-check: no stub leakage or stale paper numbers detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
