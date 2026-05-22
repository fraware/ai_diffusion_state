"""Fail if city-resolution overrides violate evidence-class hygiene rules."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

from diffusion_state.geo_evidence import validate_evidence_hygiene
from diffusion_state.smart_factory_overrides import load_city_overrides
from diffusion_state.utils import PROJECT_ROOT

REGISTER = PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"


def main() -> int:
    overrides = load_city_overrides()
    clean_path = PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    if not overrides.empty and clean_path.exists():
        clean = pd.read_csv(clean_path)
        if "source_url" in clean.columns:
            src_map = clean.set_index("project_id")["source_url"]
            overrides = overrides.assign(
                source_url=overrides["project_id"].map(lambda p: str(src_map.get(p, "")))
            )
    errors = validate_evidence_hygiene(overrides, source_url_col="source_url")

    if not REGISTER.exists():
        print("WARN: city_resolution_register.csv missing — run geo-audit first")
    else:
        reg = pd.read_csv(REGISTER)
        ext = reg[reg["resolution_class"] == "external_evidence_verified"]
        if len(ext) and (ext["evidence_url"].str.contains("solarbe|jlts", case=False, na=False)).all():
            errors.append("all external_evidence_verified rows still use list-page URLs in register")

    if errors:
        print("GEO EVIDENCE HYGIENE FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK geo evidence hygiene")
    if not overrides.empty and "resolution_class" in overrides.columns:
        print(overrides["resolution_class"].value_counts().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
