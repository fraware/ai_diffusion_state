"""Apply Engineer B audit / external-verification inputs to city-resolution seed."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.geo_evidence import (
    classify_resolution_class,
    evidence_url_for_class,
    is_external_evidence_url,
    normalize_evidence_type,
    validate_evidence_hygiene,
)
from diffusion_state.smart_factory_overrides import OVERRIDE_COLUMNS, load_city_overrides
from diffusion_state.utils import PROJECT_ROOT, write_csv

SEED_PATH = PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
QUEUE_PATH = PROJECT_ROOT / "data" / "interim" / "external_verification_queue.csv"
AUDIT_PATH = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"


def _load_seed() -> pd.DataFrame:
    df = load_city_overrides(SEED_PATH)
    if df.empty:
        return pd.DataFrame(columns=OVERRIDE_COLUMNS)
    for c in OVERRIDE_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df


def apply_external_verification_queue(
    queue_path: Path | None = None,
    seed_path: Path | None = None,
) -> tuple[pd.DataFrame, int]:
    """Merge filled external URLs from queue into override seed."""
    queue_path = queue_path or QUEUE_PATH
    seed_path = seed_path or SEED_PATH
    if not queue_path.exists():
        return _load_seed(), 0

    queue = pd.read_csv(queue_path)
    url_col = "external_evidence_url"
    if url_col not in queue.columns:
        return _load_seed(), 0

    filled = queue[queue[url_col].fillna("").astype(str).str.strip() != ""]
    if filled.empty:
        return _load_seed(), 0

    seed = _load_seed()
    by_pid = {r["project_id"]: r for _, r in seed.iterrows()} if not seed.empty else {}
    clean = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv")
    src_by_pid = clean.set_index("project_id")["source_url"].to_dict() if "source_url" in clean.columns else {}

    n = 0
    for _, row in filled.iterrows():
        pid = row["project_id"]
        ext_url = str(row[url_col]).strip()
        ext_type = str(row.get("external_evidence_type", "company_site_registry")).strip()
        source_url = str(src_by_pid.get(pid, ""))
        if not is_external_evidence_url(ext_url, source_url):
            continue
        et = normalize_evidence_type(ext_type, ext_url, source_url)
        rc = "external_evidence_verified"
        ev = evidence_url_for_class(rc, ext_url, source_url, external_url=ext_url)
        note = str(row.get("audit_notes", "")).strip() or "External verification applied from queue."
        by_pid[pid] = {
            "project_id": pid,
            "city": row["city"],
            "province": row["province"],
            "city_confidence": "high",
            "notes": note,
            "override_source": "external_verification_queue",
            "resolution_class": rc,
            "evidence_type": et,
            "evidence_url": ev,
            "external_evidence_url": ext_url,
            "reviewer": str(row.get("reviewer", "")),
            "review_date": str(row.get("review_date", "")),
        }
        n += 1

    out = pd.DataFrame(list(by_pid.values()))
    for c in OVERRIDE_COLUMNS:
        if c not in out.columns:
            out[c] = ""
    out = out[[c for c in OVERRIDE_COLUMNS if c in out.columns]]
    write_csv(out, seed_path)
    errs = validate_evidence_hygiene(out)
    if errs:
        raise ValueError("Hygiene failed after external verification apply: " + "; ".join(errs[:5]))
    return out, n


def apply_audit_corrections(
    audit_path: Path | None = None,
    seed_path: Path | None = None,
) -> tuple[pd.DataFrame, int]:
    """Apply auditor incorrect decisions with corrected_city to override seed."""
    audit_path = audit_path or AUDIT_PATH
    seed_path = seed_path or SEED_PATH
    if not audit_path.exists():
        return _load_seed(), 0

    audit = pd.read_csv(audit_path)
    fixes = audit[audit["auditor_decision"].astype(str) == "incorrect"].copy()
    fixes = fixes[fixes["corrected_city"].fillna("").astype(str).str.strip() != ""]
    if fixes.empty:
        return _load_seed(), 0

    seed = _load_seed()
    by_pid = {r["project_id"]: dict(r) for _, r in seed.iterrows()} if not seed.empty else {}
    clean = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv")
    src_by_pid = clean.set_index("project_id")["source_url"].to_dict()

    n = 0
    for _, row in fixes.iterrows():
        pid = row["project_id"]
        city = str(row["corrected_city"]).strip()
        prov = str(row.get("corrected_province", row.get("assigned_province", ""))).strip()
        source_url = str(src_by_pid.get(pid, ""))
        et = str(row.get("evidence_type", "auditor_correction"))
        rc = classify_resolution_class(et, str(row.get("evidence_url", "")), source_url)
        note = str(row.get("audit_notes", "")).strip() or "Auditor correction from stratified sample."
        by_pid[pid] = {
            "project_id": pid,
            "city": city,
            "province": prov,
            "city_confidence": "high",
            "notes": note,
            "override_source": "audit_sample_correction",
            "resolution_class": rc,
            "evidence_type": et,
            "evidence_url": str(row.get("evidence_url", source_url)),
            "external_evidence_url": "",
        }
        n += 1

    seed = pd.DataFrame(list(by_pid.values()))
    for c in OVERRIDE_COLUMNS:
        if c not in seed.columns:
            seed[c] = ""
    seed = seed[[c for c in OVERRIDE_COLUMNS if c in seed.columns]]
    write_csv(seed, seed_path)
    return seed, n
