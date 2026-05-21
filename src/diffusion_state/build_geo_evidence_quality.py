from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.audited_city_resolution import infer_audited_resolution
from diffusion_state.geo_evidence import (
    classify_resolution_class,
    evidence_url_for_class,
    normalize_evidence_type,
)
from diffusion_state.smart_factory_overrides import load_city_overrides
from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_TABLES = PROJECT_ROOT / "outputs" / "tables"
AUDIT_DIR = PROJECT_ROOT / "data" / "audit"


def _resolution_from_clean_row(row: pd.Series, override: pd.Series | None) -> dict:
    source_url = str(row.get("source_url", ""))
    if override is not None:
        et = normalize_evidence_type(
            str(override.get("evidence_type", "")),
            str(override.get("evidence_url", "")),
            source_url,
        )
        rc = str(override.get("resolution_class", "")).strip()
        if not rc:
            rc = classify_resolution_class(et, str(override.get("evidence_url", "")), source_url)
        ev_url = evidence_url_for_class(
            rc,
            str(override.get("evidence_url", "")),
            source_url,
            external_url=str(override.get("external_evidence_url", "")),
        )
        return {
            "resolution_class": rc,
            "evidence_type": et,
            "evidence_url": ev_url,
        }

    notes = str(row.get("notes", ""))
    parse_method = str(row.get("parse_method", ""))
    if "direct municipality" in notes or "prefecture-level city" in notes:
        et = "miit_location_field"
        rc = "official_location_exact"
        return {
            "resolution_class": rc,
            "evidence_type": et,
            "evidence_url": evidence_url_for_class(rc, source_url, source_url),
        }

    inferred = infer_audited_resolution(
        location_raw=str(row.get("location_raw", "")),
        firm_name_zh=str(row["firm_name_zh"]),
        project_name_zh=str(row.get("project_name_zh", "")),
        province=str(row["province"]),
        source_url=source_url,
    )
    if inferred:
        rc = classify_resolution_class(inferred.evidence_type, inferred.evidence_url, source_url)
        et = normalize_evidence_type(inferred.evidence_type, inferred.evidence_url, source_url)
        return {
            "resolution_class": rc,
            "evidence_type": et,
            "evidence_url": evidence_url_for_class(rc, inferred.evidence_url, source_url),
        }

    if row["city"] != "unknown":
        return {
            "resolution_class": "rule_based_text_inference",
            "evidence_type": parse_method or "parser_default",
            "evidence_url": source_url,
        }
    return {
        "resolution_class": "unknown",
        "evidence_type": "",
        "evidence_url": "",
    }


def build_city_resolution_register(
    clean_path: Path | None = None,
    out_path: Path | None = None,
) -> pd.DataFrame:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    clean = pd.read_csv(clean_path)
    overrides = load_city_overrides()
    omap = overrides.set_index("project_id") if not overrides.empty else None

    rows = []
    for _, row in clean.iterrows():
        ov = omap.loc[row["project_id"]] if omap is not None and row["project_id"] in omap.index else None
        meta = _resolution_from_clean_row(row, ov)
        rows.append(
            {
                "project_id": row["project_id"],
                "firm_name_zh": row["firm_name_zh"],
                "project_name_zh": row.get("project_name_zh", ""),
                "city": row["city"],
                "province": row["province"],
                "source_url": row.get("source_url", ""),
                "manual_override_flag": row.get("manual_override_flag", 0),
                **meta,
            }
        )
    reg = pd.DataFrame(rows)
    write_csv(reg, out_path)
    return reg


def build_table_geo_evidence_quality(
    register_path: Path | None = None,
) -> pd.DataFrame:
    register_path = register_path or PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    if not register_path.exists():
        build_city_resolution_register()
    reg = pd.read_csv(register_path)
    resolved = reg[reg["city"] != "unknown"].copy()
    source_urls = resolved["source_url"].fillna("").astype(str)

    def _is_list_only(urls: pd.Series) -> pd.Series:
        from diffusion_state.geo_evidence import is_smart_factory_list_url

        return urls.fillna("").map(lambda u: is_smart_factory_list_url(u) or u == "")

    from diffusion_state.geo_evidence import is_smart_factory_list_url

    resolved["source_list_url_only"] = resolved["evidence_url"].fillna("").map(
        lambda u: is_smart_factory_list_url(u) or not str(u).strip()
    )
    total = len(resolved)
    out = (
        resolved.groupby(["resolution_class", "evidence_type"], as_index=False)
        .size()
        .rename(columns={"size": "n_projects"})
    )
    out["share_projects"] = out["n_projects"] / total if total else 0.0
    list_only = (
        resolved.groupby(["resolution_class", "evidence_type"])["source_list_url_only"]
        .sum()
        .reset_index()
        .rename(columns={"source_list_url_only": "n_with_source_list_url_only"})
    )
    out = out.merge(list_only, on=["resolution_class", "evidence_type"], how="left")
    out["n_with_external_url"] = out["n_projects"] - out["n_with_source_list_url_only"]

    class_only = (
        resolved.groupby("resolution_class", as_index=False)
        .size()
        .rename(columns={"size": "n_projects"})
    )
    class_only["evidence_type"] = "_all"
    class_only["share_projects"] = class_only["n_projects"] / total if total else 0.0
    lo = (
        resolved.groupby("resolution_class")["source_list_url_only"]
        .sum()
        .reset_index()
        .rename(columns={"source_list_url_only": "n_with_source_list_url_only"})
    )
    class_only = class_only.merge(lo, on="resolution_class", how="left")
    class_only["n_with_external_url"] = class_only["n_projects"] - class_only["n_with_source_list_url_only"]

    detail = out.copy()
    out = pd.concat([class_only, detail], ignore_index=True)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_16_geo_evidence_quality.csv")
    return out


def build_table_resolution_class_summary(register_path: Path | None = None) -> pd.DataFrame:
    """One-row-per-class summary for paper text (503 resolved split)."""
    register_path = register_path or PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    if not register_path.exists():
        build_city_resolution_register()
    reg = pd.read_csv(register_path)
    resolved = reg[reg["city"] != "unknown"]
    total = len(resolved)
    rows = []
    for rc, n in resolved["resolution_class"].value_counts().items():
        rows.append(
            {
                "resolution_class": rc,
                "n_projects": int(n),
                "share_of_resolved": int(n) / total if total else 0.0,
            }
        )
    return pd.DataFrame(rows)


def build_geo_sample_audit_template(
    register_path: Path | None = None,
    audit_path: Path | None = None,
    n_rule: int = 50,
    n_external: int = 30,
    n_official: int = 20,
    seed: int = 20260520,
) -> pd.DataFrame:
    register_path = register_path or PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    audit_path = audit_path or AUDIT_DIR / "city_resolution_sample_audit.csv"
    if not register_path.exists():
        build_city_resolution_register()

    reg = pd.read_csv(register_path)
    reg = reg[reg["city"] != "unknown"]
    samples = []
    for rc, n in (
        ("rule_based_text_inference", n_rule),
        ("external_evidence_verified", n_external),
        ("official_location_exact", n_official),
    ):
        pool = reg[reg["resolution_class"] == rc]
        if pool.empty:
            continue
        take = min(n, len(pool))
        samples.append(pool.sample(n=take, random_state=seed))
    if not samples:
        audit = pd.DataFrame()
    else:
        audit = pd.concat(samples, ignore_index=True)
    audit = audit.rename(
        columns={
            "city": "assigned_city",
            "province": "assigned_province",
        }
    )
    for col in (
        "auditor_decision",
        "corrected_city",
        "corrected_province",
        "audit_notes",
        "auditor",
        "audit_date",
    ):
        audit[col] = ""
    cols = [
        "project_id",
        "firm_name_zh",
        "project_name_zh",
        "assigned_city",
        "assigned_province",
        "resolution_class",
        "evidence_type",
        "evidence_url",
        "auditor_decision",
        "corrected_city",
        "corrected_province",
        "audit_notes",
        "auditor",
        "audit_date",
    ]
    audit = audit[[c for c in cols if c in audit.columns]]
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(audit, audit_path)
    return audit


def build_table_geo_audit_error_rate(audit_path: Path | None = None) -> pd.DataFrame:
    audit_path = audit_path or AUDIT_DIR / "city_resolution_sample_audit.csv"
    if not audit_path.exists():
        build_geo_sample_audit_template()

    audit = pd.read_csv(audit_path)
    rows = []
    for rc, grp in audit.groupby("resolution_class"):
        n = len(grp)
        decisions = grp["auditor_decision"].fillna("").astype(str).str.strip()
        counts = {d: int((decisions == d).sum()) for d in decisions.unique() if d}
        incorrect = counts.get("incorrect", 0)
        rows.append(
            {
                "resolution_class": rc,
                "sampled_rows": n,
                "confirmed": counts.get("confirmed", 0),
                "incorrect": incorrect,
                "uncertain": counts.get("uncertain", 0),
                "insufficient_evidence": counts.get("insufficient_evidence", 0),
                "estimated_error_rate": incorrect / n if n else np.nan,
                "audit_status": "pending" if decisions.eq("").all() else "completed",
            }
        )
    out = pd.DataFrame(rows)
    OUTPUT_TABLES.mkdir(parents=True, exist_ok=True)
    write_csv(out, OUTPUT_TABLES / "table_17_geo_audit_error_rate.csv")
    return out
