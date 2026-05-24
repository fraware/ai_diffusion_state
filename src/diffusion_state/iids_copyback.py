"""Verify cloud VM copy-back artifacts on the control laptop."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from diffusion_state.iids_geo_join import discover_geography_supplement, is_geography_template_path
from diffusion_state.iids_paths import (
    DEFAULT_IIDS_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
    PATENT_KEYS_FOR_GEO_OUTPUT,
)
from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR
from diffusion_state.utils import PROJECT_ROOT

MANIFEST_DRAFT = RAW_PATENTS_DIR / "patent_source_manifest_draft.csv"
P0_DIAG = PROJECT_ROOT / "outputs" / "tables" / "table_P0_patent_export_schema_diagnostics.csv"
VERIFY_JSON = PROJECT_ROOT / "outputs" / "tables" / "table_P8c_iids_copyback_verification.json"

MIN_IIDS_ROWS = 500
MIN_UNIQUE_PATENT_IDS = 500


@dataclass
class ArtifactCheck:
    path: Path
    present: bool
    size_bytes: int
    rows: int | None = None
    sha256: str = ""
    issue: str = ""

    def to_dict(self) -> dict:
        return {
            "path": str(self.path.relative_to(PROJECT_ROOT)),
            "present": self.present,
            "size_bytes": self.size_bytes,
            "rows": self.rows,
            "sha256": self.sha256[:16] + "..." if self.sha256 else "",
            "issue": self.issue,
        }


@dataclass
class CopybackVerification:
    ready_for_geography_procurement: bool
    ready_for_evidence_chain: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifacts: list[ArtifactCheck] = field(default_factory=list)
    iids_rows: int = 0
    unique_patent_ids: int = 0
    geography_present: bool = False
    geography_is_template: bool = False
    manifest_fill_me_count: int = 0
    recommended_next: str = ""

    def to_dict(self) -> dict:
        return {
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "ready_for_geography_procurement": self.ready_for_geography_procurement,
            "ready_for_evidence_chain": self.ready_for_evidence_chain,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "iids_rows": self.iids_rows,
            "unique_patent_ids": self.unique_patent_ids,
            "geography_present": self.geography_present,
            "geography_is_template": self.geography_is_template,
            "manifest_fill_me_count": self.manifest_fill_me_count,
            "recommended_next": self.recommended_next,
        }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def _check_csv(path: Path, *, min_rows: int = 0) -> ArtifactCheck:
    if not path.exists():
        return ArtifactCheck(path=path, present=False, size_bytes=0, issue="missing")
    rows = _csv_rows(path)
    issue = ""
    if min_rows and rows < min_rows:
        issue = f"only {rows} rows (need >= {min_rows})"
    return ArtifactCheck(
        path=path,
        present=True,
        size_bytes=path.stat().st_size,
        rows=rows,
        sha256=_sha256(path),
        issue=issue,
    )


def _count_manifest_fill_me() -> int:
    if not MANIFEST_DRAFT.exists():
        return 0
    text = MANIFEST_DRAFT.read_text(encoding="utf-8", errors="replace")
    return text.upper().count("FILL_ME")


def verify_copyback_artifacts() -> CopybackVerification:
    blockers: list[str] = []
    warnings: list[str] = []

    checks = [
        _check_csv(DEFAULT_IIDS_OUTPUT, min_rows=MIN_IIDS_ROWS),
        _check_csv(MANIFEST_DRAFT, min_rows=1),
        _check_csv(PATENT_KEYS_FOR_GEO_OUTPUT, min_rows=1),
        _check_csv(FILTERED_PATENT_IDS_FOR_GEO_OUTPUT, min_rows=1),
        _check_csv(P0_DIAG, min_rows=0),
    ]

    iids_rows = checks[0].rows or 0
    if checks[0].issue:
        blockers.append(f"IIDS CSV: {checks[0].issue}")
    if not checks[0].present:
        blockers.append("Missing production IIDS CSV from cloud copy-back")

    keys_rows = checks[2].rows or 0
    if checks[2].present and keys_rows < (checks[0].rows or 0) * 0.5:
        warnings.append("Patent keys export has fewer rows than expected vs IIDS CSV")

    unique_ids = 0
    if FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.exists():
        import pandas as pd

        keys = pd.read_csv(FILTERED_PATENT_IDS_FOR_GEO_OUTPUT, usecols=["patent_id"])
        unique_ids = int(keys["patent_id"].astype(str).str.strip().nunique())
        if unique_ids < MIN_UNIQUE_PATENT_IDS:
            blockers.append(f"Only {unique_ids} unique patent IDs in geography keys file")

    geo = discover_geography_supplement()
    geo_present = bool(geo and geo.exists())
    geo_template = bool(geo and is_geography_template_path(geo))

    fill_me = _count_manifest_fill_me()
    if fill_me:
        warnings.append(f"patent_source_manifest_draft.csv has {fill_me} FILL_ME token(s) to resolve")

    for chk in checks:
        if chk.issue and chk.path != DEFAULT_IIDS_OUTPUT:
            warnings.append(f"{chk.path.name}: {chk.issue}")

    ready_geo = bool(
        checks[0].present
        and not checks[0].issue
        and checks[2].present
        and unique_ids >= MIN_UNIQUE_PATENT_IDS
    )
    ready_evidence = ready_geo and geo_present and not geo_template and fill_me == 0

    if ready_evidence:
        nxt = "make atlas-iids-control-evidence-chain"
    elif ready_geo and not geo_present:
        nxt = (
            "python scripts/71_geography_procurement_brief.py; "
            "build cnipa_patent_geography_2015_2024.csv; make atlas-iids-control-evidence-chain"
        )
    elif ready_geo:
        nxt = "Replace geography template with real cnipa_patent_geography_2015_2024.csv"
    else:
        nxt = "Complete cloud VM full-convert and copy-back tarball to this repo"

    return CopybackVerification(
        ready_for_geography_procurement=ready_geo,
        ready_for_evidence_chain=ready_evidence,
        blockers=blockers,
        warnings=warnings,
        artifacts=checks,
        iids_rows=iids_rows,
        unique_patent_ids=unique_ids,
        geography_present=geo_present,
        geography_is_template=geo_template,
        manifest_fill_me_count=fill_me,
        recommended_next=nxt,
    )


def write_copyback_verification() -> dict:
    report = verify_copyback_artifacts()
    VERIFY_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = report.to_dict()
    VERIFY_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload
