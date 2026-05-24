from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.patent_raw_sources import (
    FIXTURES_DIR,
    MANIFEST_COLUMNS,
    MANIFEST_PATH,
    RAW_PATENTS_DIR,
    is_excluded_evidence_path,
    is_fixture_basename,
    list_evidence_patent_csv_files,
    relative_source_file,
)
from diffusion_state.utils import PROJECT_ROOT


def load_patent_source_manifest(path: Path | None = None) -> pd.DataFrame:
    path = path or MANIFEST_PATH
    if not path.exists():
        return pd.DataFrame(columns=MANIFEST_COLUMNS)
    df = pd.read_csv(path)
    for col in MANIFEST_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[MANIFEST_COLUMNS]


def _manifest_evidence_rows(manifest: pd.DataFrame) -> pd.DataFrame:
    if manifest.empty:
        return manifest
    pub = manifest["proprietary_or_public"].astype(str).str.strip().str.lower()
    return manifest[~pub.isin({"fixture", "repository_fixture", "test_fixture", "quarantined"})]


def validate_patent_source_manifest() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.exists():
        errors.append(
            "missing data/raw/patents/patent_source_manifest.csv — add manifest row for each real export"
        )
        return errors

    manifest = load_patent_source_manifest()
    if manifest.empty:
        errors.append("patent_source_manifest.csv has no rows")
        return errors

    evidence_files = list_evidence_patent_csv_files()
    evidence_rows = _manifest_evidence_rows(manifest)

    for _, row in evidence_rows.iterrows():
        rel = str(row["source_file"]).strip()
        if not rel:
            errors.append("manifest row missing source_file")
            continue
        fp = RAW_PATENTS_DIR / rel.replace("\\", "/")
        if not fp.exists():
            errors.append(f"manifest source_file missing on disk: {rel}")
            continue
        try:
            n_rows = len(pd.read_csv(fp, low_memory=False))
        except Exception as exc:
            errors.append(f"cannot read manifest source_file {rel}: {exc}")
            continue
        expected = row.get("record_count")
        try:
            expected_n = int(expected)
        except (TypeError, ValueError):
            errors.append(f"manifest record_count invalid for {rel}: {expected}")
            continue
        if expected_n != n_rows:
            errors.append(
                f"manifest record_count mismatch for {rel}: manifest={expected_n}, file={n_rows}"
            )

    for fp in evidence_files:
        rel = relative_source_file(fp)
        manifest_files = set(evidence_rows["source_file"].astype(str).str.strip())
        if rel not in manifest_files:
            errors.append(
                f"evidence patent file {rel} has no non-fixture manifest row in patent_source_manifest.csv"
            )

    fixture_rows = manifest[
        manifest["proprietary_or_public"].astype(str).str.strip().str.lower().isin(
            {"fixture", "repository_fixture", "test_fixture", "quarantined"}
        )
    ]
    for _, row in fixture_rows.iterrows():
        rel = str(row["source_file"]).strip()
        fp = RAW_PATENTS_DIR / rel.replace("\\", "/")
        if fp.exists() and not is_excluded_evidence_path(fp):
            errors.append(
                f"fixture file {rel} is not quarantined under data/raw/patents/fixtures/"
            )

    if not evidence_files:
        # No real exports yet — manifest documents quarantined fixtures only.
        for _, row in manifest.iterrows():
            rel = str(row["source_file"]).strip()
            pub = str(row.get("proprietary_or_public", "")).strip().lower()
            if pub not in {"fixture", "repository_fixture", "test_fixture", "quarantined"}:
                errors.append(
                    f"manifest lists non-fixture source {rel} but file is absent from evidence path"
                )
        return errors

    if evidence_files and evidence_rows.empty:
        errors.append("evidence patent CSVs present but manifest has no non-fixture rows")

    return errors


def write_template_manifest(include_fixture_rows: bool = True) -> pd.DataFrame:
    """Ensure manifest exists with quarantined fixture documentation."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    if include_fixture_rows:
        for name in ("industrial_ai_patent_records.csv", "cnipa_micro.csv", "patent_database.csv"):
            fp = FIXTURES_DIR / name
            count = 0
            if fp.exists():
                try:
                    count = len(pd.read_csv(fp, low_memory=False))
                except Exception:
                    count = 0
            rows.append(
                {
                    "source_file": f"fixtures/{name}",
                    "source_platform": "repository_fixture",
                    "export_date": "",
                    "export_owner": "engineering",
                    "query_group": "fixture",
                    "query_string": "",
                    "year_min": 2015,
                    "year_max": 2024,
                    "jurisdiction_filter": "CN",
                    "record_count": count,
                    "contains_applicant_address": True,
                    "contains_city": True,
                    "contains_abstract": True,
                    "contains_claims": True,
                    "license_or_access_note": "tests only; do not use for evidence builds",
                    "proprietary_or_public": "quarantined",
                    "notes": "Excluded from Atlas evidence ingest by patent_raw_sources.py",
                }
            )

    df = pd.DataFrame(rows, columns=MANIFEST_COLUMNS)
    if MANIFEST_PATH.exists():
        existing = load_patent_source_manifest()
        real = _manifest_evidence_rows(existing)
        if not real.empty:
            df = pd.concat([df, real], ignore_index=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(MANIFEST_PATH, index=False)
    return df
