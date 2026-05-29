"""Infer university HQ city from province/region tokens in English IIDS applicant names."""
from __future__ import annotations

import re

from diffusion_state.china_city_gazetteer import first_applicant_name
from diffusion_state.region_anchors import single_region_anchor

_SKIP_UNIV_MARKERS = frozenset(
    {
        "INTERNATIONAL",
        "GLOBAL",
        "WORLD",
        "OPEN",
        "CITYU",
        "HONG KONG",
        "MACAU",
        "TAIWAN",
        "NATIONAL DONG HWA",
    }
)

_UNIV_PREFIX = re.compile(r"^UNIV\s+", re.IGNORECASE)


def infer_university_hq_from_applicant_name(applicant_name: str) -> dict[str, str] | None:
    """
    High-precision rule: UNIV + single region anchor -> provincial/campus anchor city.
    Does not fuzzy-match; skips ambiguous multi-anchor names.
    """
    first = first_applicant_name(applicant_name)
    if not _UNIV_PREFIX.match(first):
        return None

    upper = re.sub(r"\s+", " ", first.upper()).strip()
    if any(m in upper for m in _SKIP_UNIV_MARKERS):
        return None

    anchor = single_region_anchor(upper)
    if not anchor:
        return None

    token, city, province = anchor
    return {
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": f"{city}, {province}, CN (university region anchor)",
        "geo_source": "IIDS applicant_name + university region anchor rules",
        "geo_match_confidence": "university_location",
        "geo_notes": (
            f"University region anchor '{token}' in applicant_name: {first[:120]}"
        ),
    }
