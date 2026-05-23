from __future__ import annotations

import json

from diffusion_state.build_paper_tables import MANIFEST_PATH, TABLE_SPECS
from diffusion_state.utils import PROJECT_ROOT


def validate_paper_tables() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.exists():
        return ["missing paper/table_manifest.json — run scripts/38_build_paper_tables.py"]

    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    by_name = {t["paper_table"]: t for t in data.get("tables", [])}

    for spec in TABLE_SPECS:
        entry = by_name.get(spec.file_name)
        if not entry:
            errors.append(f"manifest missing {spec.file_name}")
            continue
        if entry.get("status") != "built":
            errors.append(f"table not built: {spec.file_name}")
            continue
        md_path = PROJECT_ROOT / entry["markdown_path"]
        if not md_path.exists():
            errors.append(f"missing markdown: {md_path.relative_to(PROJECT_ROOT)}")

    sub = PROJECT_ROOT / "paper" / "draft_v1_submission.md"
    if sub.exists():
        text = sub.read_text(encoding="utf-8")
        if "## Tables (paper/main_tables)" not in text:
            errors.append("draft_v1_submission.md missing embedded tables section — run make export-submission")
        if "Table I" in text and "appendix-only" not in text.lower() and "not EPS" not in text:
            errors.append("Table I appendix disclaimer missing from submission draft")
    return errors
