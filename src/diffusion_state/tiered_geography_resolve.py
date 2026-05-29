"""Resolve tiered applicant geography for one patent row (all inference tiers)."""
from __future__ import annotations

from diffusion_state.applicant_exact_aliases import geography_from_exact_alias
from diffusion_state.applicant_name_parsing import iter_applicant_names
from diffusion_state.china_city_gazetteer import geography_from_applicant_name
from diffusion_state.corporate_region_inference import infer_corporate_hq_from_applicant_name
from diffusion_state.top_applicant_institutions import geography_from_institution_registry
from diffusion_state.university_region_inference import infer_university_hq_from_applicant_name

EXACT_CONFIDENCE_PREFIXES = (
    "exact_publication_number",
    "exact_publication_number_address_parsed",
)

UNRESOLVED_LABEL = "unresolved"


def _non_empty(val: str) -> bool:
    return bool(str(val or "").strip())


def _is_exact_tier(confidence: str) -> bool:
    c = str(confidence or "").strip()
    return any(c.startswith(p) for p in EXACT_CONFIDENCE_PREFIXES) and c != "not_found"


def _row_from_manual(name: str, manual: dict[str, str]) -> dict[str, str]:
    conf = str(manual.get("geo_match_confidence") or "").strip()
    if not conf or conf == "ambiguous_unresolved":
        conf = "manually_curated_top_applicant"
    city = str(manual.get("applicant_city") or "").strip()
    province = str(manual.get("applicant_province") or "").strip()
    source_url = str(manual.get("source_url") or "").strip()
    notes = str(manual.get("notes") or "").strip()
    return {
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": f"{city}, {province}, CN (curated top applicant)",
        "geo_source": source_url or "top_applicant_city_map.csv",
        "geo_match_confidence": conf,
        "geo_notes": notes or f"Curated mapping for applicant: {name[:120]}",
    }


def _with_coapplicant_note(geo: dict[str, str], matched_name: str, first_name: str) -> dict[str, str]:
    if matched_name == first_name:
        return geo
    out = dict(geo)
    base = str(out.get("geo_notes") or "")
    out["geo_notes"] = f"{base} Co-applicant match: {matched_name[:100]}.".strip()
    return out


def resolve_single_applicant(
    applicant_name: str,
    *,
    top_map: dict[str, dict[str, str]],
) -> tuple[dict[str, str], str]:
    """Resolve geography for one applicant token (no external exact tier)."""
    name = str(applicant_name or "").strip()
    if not name:
        return {}, UNRESOLVED_LABEL

    manual = top_map.get(name, {})
    if manual:
        merged = _row_from_manual(name, manual)
        return merged, str(merged.get("geo_match_confidence") or "manually_curated_top_applicant")

    for resolver in (
        geography_from_exact_alias,
        geography_from_institution_registry,
        infer_corporate_hq_from_applicant_name,
        infer_university_hq_from_applicant_name,
    ):
        geo = resolver(name)
        if geo and _non_empty(geo.get("applicant_city", "")):
            conf = str(geo.get("geo_match_confidence") or "official_headquarters_page")
            return geo, conf

    token_geo = geography_from_applicant_name(name)
    if _non_empty(token_geo.get("applicant_city", "")):
        return token_geo, "applicant_name_city_token"

    return {}, UNRESOLVED_LABEL


def resolve_tiered_geography(
    *,
    patent_id: str,
    applicant_name: str,
    external: dict[str, dict[str, str]],
    top_map: dict[str, dict[str, str]],
) -> tuple[dict[str, str], str]:
    """Full merge priority including external exact and co-applicant scan."""
    ext = external.get(patent_id, {})
    ext_conf = str(ext.get("geo_match_confidence") or "").strip()
    if ext and _is_exact_tier(ext_conf) and _non_empty(str(ext.get("applicant_city", ""))):
        merged = {
            c: str(ext.get(c, "") or "").strip()
            for c in (
                "applicant_city",
                "applicant_province",
                "applicant_address",
                "geo_source",
                "geo_match_confidence",
                "geo_notes",
            )
        }
        return merged, str(merged.get("geo_match_confidence") or "exact_publication_number")

    names = iter_applicant_names(applicant_name)
    if not names:
        return {}, UNRESOLVED_LABEL

    first = names[0]
    for candidate in names:
        geo, tier = resolve_single_applicant(candidate, top_map=top_map)
        if tier != UNRESOLVED_LABEL:
            return _with_coapplicant_note(geo, candidate, first), tier

    return {}, UNRESOLVED_LABEL
