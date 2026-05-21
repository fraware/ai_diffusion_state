from __future__ import annotations

import re
from urllib.parse import urlparse

OFFICIAL_LOCATION_TYPES = frozenset({"miit_location_field"})

RULE_BASED_TYPES = frozenset(
    {
        "firm_province_county",
        "firm_parenthetical",
        "firm_embedded_city_token",
        "project_embedded_city_token",
        "project_branch_city",
        "project_name_city",
        "firm_registry_match",
    }
)

# Legacy registry labels — treated as curated inference unless a non-list external URL is set.
REGISTRY_LEGACY_TYPES = frozenset(
    {
        "company_annual_report",
        "company_site_registry",
        "industrial_park_page",
        "project_registry",
        "firm_registry_match",
    }
)

EXTERNAL_EVIDENCE_TYPES = frozenset(
    {
        "company_annual_report",
        "company_site_registry",
        "industrial_park_page",
        "project_registry",
    }
)

LIST_PAGE_HOST_PATTERNS = (
    r"solarbe\.com",
    r"jlts\.com\.cn",
)


def _host(url: str) -> str:
    try:
        return urlparse(str(url).strip()).netloc.lower()
    except Exception:
        return ""


def is_smart_factory_list_url(url: str) -> bool:
    host = _host(url)
    if not host:
        return True
    return any(re.search(pat, host) for pat in LIST_PAGE_HOST_PATTERNS)


def is_external_evidence_url(evidence_url: str, source_url: str) -> bool:
    ev = str(evidence_url or "").strip()
    if not ev:
        return False
    if ev == str(source_url or "").strip():
        return False
    return not is_smart_factory_list_url(ev)


def normalize_evidence_type(evidence_type: str, evidence_url: str, source_url: str) -> str:
    """Map legacy registry evidence labels to firm_registry_match when URL is not external."""
    et = str(evidence_type or "").strip()
    if et in REGISTRY_LEGACY_TYPES and not is_external_evidence_url(evidence_url, source_url):
        return "firm_registry_match"
    return et


def classify_resolution_class(
    evidence_type: str,
    evidence_url: str,
    source_url: str,
) -> str:
    et = normalize_evidence_type(evidence_type, evidence_url, source_url)
    if et in OFFICIAL_LOCATION_TYPES:
        return "official_location_exact"
    if et in EXTERNAL_EVIDENCE_TYPES and is_external_evidence_url(evidence_url, source_url):
        return "external_evidence_verified"
    return "rule_based_text_inference"


def validate_evidence_hygiene(
    overrides: "pd.DataFrame",
    *,
    source_url_col: str = "source_url",
) -> list[str]:
    """Return human-readable violations (empty if reviewer-safe)."""
    import pandas as pd

    errors: list[str] = []
    if overrides is None or overrides.empty:
        return errors

    if "resolution_class" not in overrides.columns:
        errors.append("overrides missing resolution_class column")
        return errors

    missing_class = overrides["resolution_class"].isna() | (
        overrides["resolution_class"].astype(str).str.strip() == ""
    )
    if missing_class.any():
        errors.append(f"{int(missing_class.sum())} override rows missing resolution_class")

    ext = overrides[overrides["resolution_class"] == "external_evidence_verified"]
    for _, row in ext.iterrows():
        ev = str(row.get("evidence_url", ""))
        ext_url = str(row.get("external_evidence_url", ""))
        src = str(row.get(source_url_col, row.get("evidence_url", "")))
        if not is_external_evidence_url(ext_url or ev, src):
            errors.append(
                f"external_evidence_verified without external URL: {row.get('project_id', '?')}"
            )

    for _, row in overrides.iterrows():
        rc = str(row.get("resolution_class", ""))
        et = str(row.get("evidence_type", ""))
        ev = str(row.get("evidence_url", ""))
        if rc == "external_evidence_verified" and et == "firm_registry_match":
            errors.append(f"registry label with external class: {row.get('project_id', '?')}")
        if rc == "rule_based_text_inference" and et in EXTERNAL_EVIDENCE_TYPES:
            if normalize_evidence_type(et, ev, ev) == "firm_registry_match":
                continue
            errors.append(
                f"rule_based row retains external evidence_type {et}: {row.get('project_id', '?')}"
            )

    legacy = overrides[
        overrides["evidence_type"].isin(
            {"company_annual_report", "company_site_registry", "project_registry"}
        )
        & (overrides["resolution_class"] != "external_evidence_verified")
    ]
    if not legacy.empty and (legacy["evidence_type"] != "firm_registry_match").any():
        n = int((legacy["evidence_type"] != "firm_registry_match").sum())
        errors.append(f"{n} rows still use legacy external evidence_type labels on list URLs")

    return errors


def evidence_url_for_class(
    resolution_class: str,
    evidence_url: str,
    source_url: str,
    external_url: str = "",
) -> str:
    """Reviewer-safe evidence_url by resolution class."""
    if resolution_class == "external_evidence_verified":
        return str(external_url or evidence_url or "").strip()
    if resolution_class == "official_location_exact":
        return str(evidence_url or source_url or "").strip()
    # Rule-based: list page is acceptable; never imply external annual report URL.
    return str(source_url or evidence_url or "").strip()
