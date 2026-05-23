from __future__ import annotations

import json

from diffusion_state.build_paper_figures import MANIFEST_PATH, PCS_FIGURES
from diffusion_state.utils import PROJECT_ROOT


def validate_paper_figures() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.exists():
        return ["missing paper/figure_manifest.json — run scripts/34_build_paper_figures.py"]

    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    figures = {f["paper_path"]: f for f in data.get("figures", [])}

    for spec in PCS_FIGURES:
        if not spec.required:
            continue
        paper_path = PROJECT_ROOT / "paper" / "figures" / spec.paper_name
        if not paper_path.exists():
            errors.append(f"missing required figure: {paper_path.relative_to(PROJECT_ROOT)}")
        entry = figures.get(f"paper/figures/{spec.paper_name}")
        if entry and entry.get("status") == "missing":
            errors.append(f"source figure missing for {spec.paper_name}")

    return errors
