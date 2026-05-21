from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.smart_factory_geo import (
    CITY_IN_TEXT_RE,
    GeoResult,
    _city_from_firm_parenthetical,
    _city_from_firm_province_county,
    _city_from_location_string,
    _load_geo_tokens,
    _prefecture_city_en,
    _province_for_prefecture_city,
    normalize_firm_name_zh,
    resolve_cn_locality,
)
from diffusion_state.utils import PROJECT_ROOT, read_yaml, write_csv

BRANCH_RE = re.compile(r"([\u4e00-\u9fff]{2,8})分公司")
CITY_IN_FIRM_RE = re.compile(r"([\u4e00-\u9fff]{2,12}市)")

# Evidence types allowed for automatic audited overrides (not HQ-only national prefix).
ALLOWED_EVIDENCE_TYPES = {
    "miit_location_field",
    "firm_province_county",
    "firm_parenthetical",
    "firm_embedded_city_token",
    "firm_registry_match",
    "project_branch_city",
    "project_name_city",
    "company_annual_report",
    "company_site_registry",
    "industrial_park_page",
    "project_registry",
    "project_embedded_city_token",
}

HQ_ONLY_PREFIX_BLOCKED = True


@dataclass(frozen=True)
class AuditedResolution:
    city: str
    province: str
    city_confidence: str
    evidence_url: str
    evidence_type: str
    notes: str


def _load_firm_registry() -> list[dict]:
    entries: list[dict] = []
    for name in ("audited_firm_city_registry.yml", "audited_firm_city_registry_supplement.yml"):
        path = PROJECT_ROOT / "configs" / name
        if path.exists():
            entries.extend(read_yaml(path).get("entries", []))
    return entries


def _province_matches(expected: str, resolved: str) -> bool:
    return expected == "unknown" or resolved == "unknown" or expected == resolved


def _from_embedded_token(firm: str, expected_province: str) -> AuditedResolution | None:
    for zh, city_en, prov_en in _load_geo_tokens():
        if zh not in firm:
            continue
        if not _province_matches(expected_province, prov_en):
            continue
        return AuditedResolution(
            city=city_en,
            province=prov_en,
            city_confidence="high",
            evidence_url="",
            evidence_type="firm_embedded_city_token",
            notes=f"City token '{zh}' in legal entity name; province-only MIIT location.",
        )
    return None


def _from_registry(firm: str, project: str, source_url: str, expected_province: str) -> AuditedResolution | None:
    text = f"{firm} {project}"
    for entry in _load_firm_registry():
        if entry["match"] not in text:
            continue
        if not _province_matches(expected_province, entry["province"]):
            continue
        return AuditedResolution(
            city=entry["city"],
            province=entry["province"],
            city_confidence="high",
            evidence_url=source_url,
            evidence_type=entry["evidence_type"],
            notes=f"{entry['note']} (registry match: {entry['match']})",
        )
    return None


def _from_branch(project: str, firm: str, source_url: str, expected_province: str) -> AuditedResolution | None:
    for text in (project, firm):
        m = BRANCH_RE.search(text or "")
        if not m:
            continue
        cn = m.group(1)
        hit = resolve_cn_locality(cn)
        if not hit:
            loc = f"{cn}市"
            city = _prefecture_city_en(loc)
            prov = _province_for_prefecture_city(loc)
        else:
            city, prov = hit
        if city and _province_matches(expected_province, prov or "unknown"):
            return AuditedResolution(
                city=city,
                province=prov or expected_province,
                city_confidence="high",
                evidence_url=source_url,
                evidence_type="project_branch_city",
                notes=f"Branch city from 分公司 pattern: {cn}",
            )
    return None


def infer_audited_resolution(
    *,
    location_raw: str,
    firm_name_zh: str,
    project_name_zh: str,
    province: str,
    source_url: str,
) -> AuditedResolution | None:
    """Infer city for province-only rows using auditable non-HQ evidence."""
    firm = normalize_firm_name_zh(firm_name_zh)
    project = str(project_name_zh or "")
    cfg = read_yaml(PROJECT_ROOT / "configs" / "province_normalization.yml")

    loc_hit = _city_from_location_string(location_raw, cfg)
    if loc_hit.city != "unknown":
        if loc_hit.city_confidence not in {"exact", "high"}:
            return None
        return AuditedResolution(
            city=loc_hit.city,
            province=loc_hit.province,
            city_confidence=loc_hit.city_confidence,
            evidence_url=source_url,
            evidence_type="miit_location_field",
            notes=loc_hit.geo_notes,
        )

    for infer, evidence_type in (
        (_city_from_firm_province_county(firm), "firm_province_county"),
        (_city_from_firm_parenthetical(firm), "firm_parenthetical"),
    ):
        if infer and infer.city != "unknown" and _province_matches(province, infer.province):
            return AuditedResolution(
                city=infer.city,
                province=infer.province if infer.province != "unknown" else province,
                city_confidence=infer.city_confidence,
                evidence_url=source_url,
                evidence_type=evidence_type,
                notes=infer.geo_notes,
            )

    branch = _from_branch(project, firm, source_url, province)
    if branch:
        return branch

    for text, ev_type in ((firm, "firm_embedded_city_token"), (project, "project_embedded_city_token")):
        token = _from_embedded_token(text, province)
        if token:
            return AuditedResolution(
                city=token.city,
                province=token.province,
                city_confidence=token.city_confidence,
                evidence_url=source_url,
                evidence_type=ev_type,
                notes=token.notes,
            )

    for match in CITY_IN_FIRM_RE.findall(firm):
        if match in {"中国市", "本市"}:
            continue
        city = _prefecture_city_en(match)
        prov = _province_for_prefecture_city(match)
        if city and _province_matches(province, prov or "unknown"):
            return AuditedResolution(
                city=city,
                province=prov or province,
                city_confidence="high",
                evidence_url=source_url,
                evidence_type="firm_embedded_city_token",
                notes=f"Prefecture in firm name: {match}",
            )

    registry = _from_registry(firm, project, source_url, province)
    if registry:
        return registry

    for match in CITY_IN_TEXT_RE.findall(project):
        if match in {"中国市", "本市"}:
            continue
        city = _prefecture_city_en(match)
        prov = _province_for_prefecture_city(match)
        if city and _province_matches(province, prov or "unknown"):
            return AuditedResolution(
                city=city,
                province=prov or province,
                city_confidence="high",
                evidence_url=source_url,
                evidence_type="project_name_city",
                notes=f"City in project name: {match}",
            )

    return None


def build_audited_city_overrides(
    clean_path: Path | None = None,
    out_path: Path | None = None,
    *,
    priority_provinces_only: bool = False,
) -> pd.DataFrame:
    """Write seed overrides for unknown-city projects with auditable evidence."""
    from diffusion_state.build_unknown_city_queue import PRIORITY_PROVINCES

    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    out_path = out_path or PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"

    clean = pd.read_csv(clean_path)
    candidates = clean.copy()
    if priority_provinces_only:
        candidates = candidates[candidates["province"].isin(PRIORITY_PROVINCES)]

    rows = []
    for _, row in candidates.iterrows():
        res = infer_audited_resolution(
            location_raw=str(row.get("location_raw", "")),
            firm_name_zh=str(row["firm_name_zh"]),
            project_name_zh=str(row.get("project_name_zh", "")),
            province=str(row["province"]),
            source_url=str(row.get("source_url", "")),
        )
        if res is None or res.city_confidence not in {"exact", "high"}:
            continue
        if res.evidence_type not in ALLOWED_EVIDENCE_TYPES:
            continue
        current_city = str(row["city"])
        if current_city not in {"unknown", res.city}:
            continue
        rows.append(
            {
                "project_id": row["project_id"],
                "city": res.city,
                "province": res.province,
                "city_confidence": res.city_confidence,
                "evidence_url": res.evidence_url or row.get("source_url", ""),
                "evidence_type": res.evidence_type,
                "notes": res.notes,
                "reviewer": "geo_audit_pipeline",
                "review_date": "2026-05-20",
                "override_source": res.evidence_type,
            }
        )

    out_df = pd.DataFrame(rows)
    if not out_df.empty:
        out_df = out_df.drop_duplicates(subset=["project_id"], keep="first")
    write_csv(out_df, out_path)
    return out_df


def apply_audited_resolution_to_geo(
    location_raw: str,
    firm_name_zh: str,
    project_name_zh: str,
    province: str,
    source_url: str,
) -> GeoResult | None:
    res = infer_audited_resolution(
        location_raw=location_raw,
        firm_name_zh=firm_name_zh,
        project_name_zh=project_name_zh,
        province=province,
        source_url=source_url,
    )
    if res is None:
        return None
    return GeoResult(res.province, res.city, res.city_confidence, res.notes)
