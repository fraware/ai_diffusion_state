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
from diffusion_state.geo_evidence import (
    classify_resolution_class,
    evidence_url_for_class,
    normalize_evidence_type,
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
    "firm_registry_match",
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
    resolution_class: str
    external_evidence_url: str = ""


def _make_resolution(
    *,
    city: str,
    province: str,
    city_confidence: str,
    evidence_type: str,
    notes: str,
    source_url: str,
    external_url: str = "",
) -> AuditedResolution:
    et = normalize_evidence_type(evidence_type, external_url or "", source_url)
    rc = classify_resolution_class(et, external_url, source_url)
    ev = evidence_url_for_class(rc, source_url, source_url, external_url=external_url)
    return AuditedResolution(
        city=city,
        province=province,
        city_confidence=city_confidence,
        evidence_url=ev,
        evidence_type=et,
        notes=notes,
        resolution_class=rc,
        external_evidence_url=external_url if rc == "external_evidence_verified" else "",
    )


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
        return _make_resolution(
            city=city_en,
            province=prov_en,
            city_confidence="high",
            evidence_type="firm_embedded_city_token",
            notes=f"City token '{zh}' in legal entity name; province-only MIIT location.",
            source_url="",
        )
    return None


def _from_registry(
    firm: str,
    project: str,
    source_url: str,
    expected_province: str,
    *,
    province_only_location: bool = False,
) -> AuditedResolution | None:
    text = f"{firm} {project}"
    for entry in _load_firm_registry():
        if entry["match"] not in text:
            continue
        if not province_only_location and not _province_matches(expected_province, entry["province"]):
            continue
        ext = str(entry.get("evidence_url", "") or entry.get("external_evidence_url", "")).strip()
        note_extra = ""
        if province_only_location and expected_province != entry["province"]:
            note_extra = f" (plant-city registry; MIIT list province={expected_province})"
        return _make_resolution(
            city=entry["city"],
            province=entry["province"],
            city_confidence="high",
            evidence_type=entry.get("evidence_type", "firm_registry_match"),
            notes=f"{entry['note']}{note_extra} (registry match: {entry['match']})",
            source_url=source_url,
            external_url=ext,
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
            return _make_resolution(
                city=city,
                province=prov or expected_province,
                city_confidence="high",
                evidence_type="project_branch_city",
                notes=f"Branch city from 分公司 pattern: {cn}",
                source_url=source_url,
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
    province_only_location = loc_hit.city == "unknown" and loc_hit.province != "unknown"
    if loc_hit.city != "unknown":
        if loc_hit.city_confidence not in {"exact", "high"}:
            return None
        return _make_resolution(
            city=loc_hit.city,
            province=loc_hit.province,
            city_confidence=loc_hit.city_confidence,
            evidence_type="miit_location_field",
            notes=loc_hit.geo_notes,
            source_url=source_url,
        )

    for infer, evidence_type in (
        (_city_from_firm_province_county(firm), "firm_province_county"),
        (_city_from_firm_parenthetical(firm), "firm_parenthetical"),
    ):
        if infer and infer.city != "unknown" and _province_matches(province, infer.province):
            return _make_resolution(
                city=infer.city,
                province=infer.province if infer.province != "unknown" else province,
                city_confidence=infer.city_confidence,
                evidence_type=evidence_type,
                notes=infer.geo_notes,
                source_url=source_url,
            )

    branch = _from_branch(project, firm, source_url, province)
    if branch:
        return branch

    for text, ev_type in ((firm, "firm_embedded_city_token"), (project, "project_embedded_city_token")):
        token = _from_embedded_token(text, province)
        if token:
            return _make_resolution(
                city=token.city,
                province=token.province,
                city_confidence=token.city_confidence,
                evidence_type=ev_type,
                notes=token.notes,
                source_url=source_url,
            )

    for match in CITY_IN_FIRM_RE.findall(firm):
        if match in {"中国市", "本市"}:
            continue
        city = _prefecture_city_en(match)
        prov = _province_for_prefecture_city(match)
        if city and _province_matches(province, prov or "unknown"):
            return _make_resolution(
                city=city,
                province=prov or province,
                city_confidence="high",
                evidence_type="firm_embedded_city_token",
                notes=f"Prefecture in firm name: {match}",
                source_url=source_url,
            )

    registry = _from_registry(
        firm, project, source_url, province, province_only_location=province_only_location
    )
    if registry:
        return registry

    for match in CITY_IN_TEXT_RE.findall(project):
        if match in {"中国市", "本市"}:
            continue
        city = _prefecture_city_en(match)
        prov = _province_for_prefecture_city(match)
        if city and _province_matches(province, prov or "unknown"):
            return _make_resolution(
                city=city,
                province=prov or province,
                city_confidence="high",
                evidence_type="project_name_city",
                notes=f"City in project name: {match}",
                source_url=source_url,
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
                "resolution_class": res.resolution_class,
                "evidence_url": res.evidence_url,
                "evidence_type": res.evidence_type,
                "external_evidence_url": res.external_evidence_url,
                "notes": res.notes,
                "reviewer": "geo_audit_pipeline",
                "review_date": "2026-05-20",
                "override_source": res.evidence_type,
            }
        )

    out_df = pd.DataFrame(rows)
    if not out_df.empty:
        out_df = out_df.drop_duplicates(subset=["project_id"], keep="first")
        from diffusion_state.geo_evidence import validate_evidence_hygiene

        violations = validate_evidence_hygiene(out_df)
        if violations:
            raise ValueError("Geo evidence hygiene failed:\n" + "\n".join(violations[:20]))
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
