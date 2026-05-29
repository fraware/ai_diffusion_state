from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from diffusion_state.git_utils import get_git_revision
from diffusion_state.utils import PROJECT_ROOT

BUNDLE_DIR = PROJECT_ROOT / "paper" / "submission_bundle"
MANIFEST_JSON = PROJECT_ROOT / "paper" / "SUBMISSION_MANIFEST.json"

BUNDLE_PATHS: tuple[str, ...] = (
    "paper/draft_v1.md",
    "paper/draft_v1_appendix.md",
    "paper/draft_v1_submission.md",
    "paper/draft_v1.tex",
    "paper/references.bib",
    "paper/citation_map.csv",
    "paper/claim_table_map.csv",
    "paper/main_table_claim_map.csv",
    "paper/pcs_gate_report.json",
    "paper/figure_manifest.json",
    "paper/table_manifest.json",
    "paper/SUBMISSION_READINESS.md",
    "paper/COVER_LETTER_DRAFT.md",
    "paper/SUBMISSION_CHECKLIST.md",
    "paper/SUBMISSION_READINESS.md",
    "paper/SUBMISSION_OWNER_BRIEF.md",
    "paper/results_memo.md",
    "paper/red_team_memo.md",
    "paper/reviewer_results_snapshot.md",
    "paper/data_appendix.md",
    "docs/model_interpretation_matrix.md",
    "docs/PCS_GATE_CHECKLIST.md",
)

BUNDLE_DIRS: tuple[str, ...] = (
    "paper/main_tables",
    "paper/figures",
    "paper/tables_md",
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_reproducibility_md() -> Path:
    path = PROJECT_ROOT / "paper" / "REPRODUCIBILITY.md"
    text = """# Reproducibility statement (PCS measurement paper)

## One-command rebuild

```powershell
make pcs
```

This runs the full measurement pipeline, syncs paper memos, builds Tables A–I, exports the submission draft, and writes `paper/pcs_gate_report.json`.

## Submission-only rebuild

```powershell
make paper-figures
make paper-tables
make export-submission
make submission-bundle
make validate-submission
python scripts/15_pcs_status.py --json
```

## Expected gate state

- `ready: true` — geo, audit, external verification, main tables
- `submission_ready: true` — figures, embedded tables, bibliography, language gates

## Software

- Python >= 3.10
- Install: `pip install -e .[dev]`
- See `pyproject.toml` for pinned dependencies

## Data not in repository

- CEPII BACI export files (optional; `make baci`)
- EPS/NBS city controls (strict Table 5 blocked until provided)
- CNIPA full patent microdata (Atlas sprint; not required for PCS paper)

## Primary artifacts for reviewers

| Artifact | Role |
|----------|------|
| `paper/draft_v1_submission.md` | Full draft with embedded tables and figures |
| `paper/main_tables/table_*.csv` | Draft-facing Tables A–I |
| `paper/claim_table_map.csv` | Claim tier traceability |
| `paper/pcs_gate_report.json` | Machine-readable gate snapshot |

## Commit hash

Record the git commit used for submission in the journal cover letter. Build manifest: `paper/SUBMISSION_MANIFEST.json`.
"""
    path.write_text(text, encoding="utf-8")
    return path


def _write_data_availability_md() -> Path:
    path = PROJECT_ROOT / "paper" / "DATA_AVAILABILITY.md"
    text = """# Data availability (PCS measurement paper)

## Public policy and list sources

- National AI innovation and development pilot zones: CSET summary and Xinhua 17-zone list (see `paper/references.bib`, `configs/sources.yml`).
- MIIT excellence-level smart-factory projects (2024 and 2025): public HTML mirrors documented in `data/raw/smart_factories/` and `configs/sources.yml`.

## Processed data in repository

After `make pcs`, the following support all main-text statistics:

- `data/processed/pilot_zones.csv`
- `data/processed/smart_factories_clean.csv`
- `data/processed/city_resolution_register.csv`
- `data/processed/analysis_city_year_panel.csv`
- `paper/main_tables/` (Tables A–I)

## Restricted or external data

- **EPS/NBS city economic controls:** not included; strict controlled adoption (Table 5) is skipped by design.
- **Appendix Table I:** partial 2024 China City Statistical Yearbook variables via ChinaUTC public fallback (`paper/main_tables/table_I_appendix_public_fallback_controls.csv`). Not equivalent to EPS/NBS.
- **BACI trade data:** optional for export-relevance descriptives; download from CEPII under their terms.

## Replication package

The directory `paper/submission_bundle/` (built by `make submission-bundle`) contains the draft, tables, figures, claim maps, and gate report for journal submission.
"""
    path.write_text(text, encoding="utf-8")
    return path


def build_submission_bundle(clean: bool = True) -> dict:
    if clean and BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)

    _write_reproducibility_md()
    _write_data_availability_md()

    files: list[dict] = []

    def _copy_file(rel: str) -> None:
        src = PROJECT_ROOT / rel
        if not src.exists():
            return
        dst = BUNDLE_DIR / rel.replace("paper/", "")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files.append(
            {
                "path": rel,
                "bundle_path": str(dst.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "bytes": src.stat().st_size,
                "sha256": _sha256(src),
            }
        )

    for rel in BUNDLE_PATHS:
        _copy_file(rel)
    _copy_file("paper/REPRODUCIBILITY.md")
    _copy_file("paper/DATA_AVAILABILITY.md")

    for rel_dir in BUNDLE_DIRS:
        src_dir = PROJECT_ROOT / rel_dir
        if not src_dir.exists():
            continue
        dst_dir = BUNDLE_DIR / rel_dir.replace("paper/", "")
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        for fp in src_dir.rglob("*"):
            if fp.is_file():
                rel = str(fp.relative_to(PROJECT_ROOT)).replace("\\", "/")
                files.append(
                    {
                        "path": rel,
                        "bundle_path": str(fp.relative_to(PROJECT_ROOT / "paper")).replace("\\", "/"),
                        "bytes": fp.stat().st_size,
                        "sha256": _sha256(fp),
                    }
                )

    revision = get_git_revision()
    manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "bundle_directory": "paper/submission_bundle",
        "git_revision": revision.get("full") or None,
        "git_revision_short": revision.get("short") or None,
        "git_dirty": bool(revision.get("dirty")),
        "n_files": len(files),
        "files": sorted(files, key=lambda x: x["path"]),
        "gates_report": "paper/pcs_gate_report.json",
        "rebuild_command": "make pcs",
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    shutil.copy2(MANIFEST_JSON, BUNDLE_DIR / "SUBMISSION_MANIFEST.json")
    return manifest
