"""Infer HQ/campus city for grid, CAS, and other corporate patterns in English IIDS names."""
from __future__ import annotations

import re

from diffusion_state.china_city_gazetteer import first_applicant_name
from diffusion_state.region_anchors import single_region_anchor

# Explicit CAS institute campuses (English IIDS applicant_name).
_CAS_INSTITUTE_LOCATIONS: dict[str, tuple[str, str, str]] = {
    "INST METAL RESEARCH CAS": ("Shenyang", "Liaoning", "Institute of Metal Research, CAS."),
    "INST ROCK & SOIL MECH CAS": ("Wuhan", "Hubei", "Institute of Rock and Soil Mechanics, CAS."),
    "INST GEOLOGY & GEOPHYSICS CAS": ("Beijing", "Beijing", "Institute of Geology and Geophysics, CAS."),
    "INST REMOTE SENSING & DIGITAL EARTH CAS": ("Beijing", "Beijing", "RADI, CAS."),
    "INST SEMICONDUCTORS CAS": ("Beijing", "Beijing", "Institute of Semiconductors, CAS."),
    "INST COMPUTING TECH CAS": ("Beijing", "Beijing", "Institute of Computing Technology, CAS."),
    "INST AUTOMATION CAS": ("Beijing", "Beijing", "Institute of Automation, CAS."),
    "INST CHEMISTRY CAS": ("Beijing", "Beijing", "Institute of Chemistry, CAS."),
    "INST PHYSICS CAS": ("Beijing", "Beijing", "Institute of Physics, CAS."),
    "INST ACOUSTICS CAS": ("Beijing", "Beijing", "Institute of Acoustics, CAS."),
    "INST PROCESS ENG CAS": ("Beijing", "Beijing", "Institute of Process Engineering, CAS."),
    "INST ELECTRICAL ENG CAS": ("Beijing", "Beijing", "Institute of Electrical Engineering, CAS."),
    "INST OPTICS & ELECTRONICS CAS": ("Changchun", "Jilin", "Changchun Institute of Optics, CAS."),
    "INST GENETICS & DEVELOPMENTAL BIOLOGY CAS": ("Beijing", "Beijing", "Institute of Genetics, CAS."),
    "INST HIGH ENERGY PHYSICS CAS": ("Beijing", "Beijing", "IHEP, CAS."),
    "INST THEORETICAL PHYSICS CAS": ("Beijing", "Beijing", "ITP, CAS."),
    "INST SOFTWARE CAS": ("Beijing", "Beijing", "Institute of Software, CAS."),
    "INST MICROBIOLOGY CAS": ("Beijing", "Beijing", "Institute of Microbiology, CAS."),
    "INST BOTANY CAS": ("Beijing", "Beijing", "Institute of Botany, CAS."),
    "INST ZOOLOGY CAS": ("Beijing", "Beijing", "Institute of Zoology, CAS."),
    "INST GEOGRAPHIC SCIENCES & NATURAL RESOURCES RES CAS": (
        "Beijing",
        "Beijing",
        "IGSNRR, CAS.",
    ),
}

_GRID_MARKERS = ("STATE GRID", "POWER GRID", "ELECTRIC POWER CO", "ELECTRIC POWER RES INST")
_CAS_SUFFIX = re.compile(r"\bCAS\b", re.IGNORECASE)
_INST_PREFIX = re.compile(r"^INST\s+", re.IGNORECASE)


def _geo_row(
    city: str,
    province: str,
    confidence: str,
    notes: str,
    address_label: str,
) -> dict[str, str]:
    return {
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": f"{city}, {province}, CN ({address_label})",
        "geo_source": "IIDS applicant_name + corporate region anchor rules",
        "geo_match_confidence": confidence,
        "geo_notes": notes,
    }


def infer_corporate_hq_from_applicant_name(applicant_name: str) -> dict[str, str] | None:
    first = first_applicant_name(applicant_name)
    if not first:
        return None

    upper = re.sub(r"\s+", " ", first.upper()).strip()

    if first in _CAS_INSTITUTE_LOCATIONS:
        city, province, notes = _CAS_INSTITUTE_LOCATIONS[first]
        return _geo_row(
            city,
            province,
            "university_location",
            notes,
            "CAS institute registry",
        )

    if _INST_PREFIX.match(first) and _CAS_SUFFIX.search(upper):
        anchor = single_region_anchor(upper)
        if anchor:
            token, city, province = anchor
            return _geo_row(
                city,
                province,
                "university_location",
                f"CAS institute regional anchor '{token}': {first[:120]}",
                "CAS institute region anchor",
            )
        return _geo_row(
            "Beijing",
            "Beijing",
            "university_location",
            f"CAS institute default Beijing campus: {first[:120]}",
            "CAS institute default Beijing",
        )

    if any(marker in upper for marker in _GRID_MARKERS):
        anchor = single_region_anchor(upper)
        if anchor:
            token, city, province = anchor
            return _geo_row(
                city,
                province,
                "official_headquarters_page",
                f"Power-grid regional anchor '{token}': {first[:120]}",
                "power grid region anchor",
            )

    if upper in {
        "CHINA SOUTHERN POWER GRID CO LTD",
        "CHINA SOUTHERN POWER GRID CO",
        "CHINA SOUTHERN POWER GRID",
    } or upper.startswith("CHINA SOUTHERN POWER GRID "):
        return _geo_row(
            "Guangzhou",
            "Guangdong",
            "official_headquarters_page",
            "China Southern Power Grid headquarters.",
            "curated power grid HQ",
        )

    if "CHINA NAT PETROLEUM" in upper or "CHINA NATIONAL PETROLEUM" in upper:
        return _geo_row(
            "Beijing",
            "Beijing",
            "official_headquarters_page",
            "CNPC group headquarters.",
            "curated petroleum HQ",
        )

    if "CHINESE ACADEMY" in upper or "CHINA ACADEMY" in upper:
        return _geo_row(
            "Beijing",
            "Beijing",
            "university_location",
            "Chinese Academy of Sciences (Beijing).",
            "CAS academy parent",
        )

    if "CHINA RAILWAY" in upper and "UNIV" not in upper:
        return _geo_row(
            "Beijing",
            "Beijing",
            "official_headquarters_page",
            "China Railway group headquarters.",
            "China Railway SOE",
        )

    if upper.startswith("CHINA STATE ") or "CHINA STATE CONSTRUCTION" in upper:
        return _geo_row(
            "Beijing",
            "Beijing",
            "official_headquarters_page",
            "Central SOE headquarters (Beijing).",
            "China central SOE",
        )

    if "NAT CT" in upper or "NATIONAL CENTER FOR" in upper or upper.startswith("NAT INST"):
        anchor = single_region_anchor(upper)
        if anchor:
            token, city, province = anchor
            return _geo_row(
                city,
                province,
                "university_location",
                f"National institute regional anchor '{token}'.",
                "national institute region",
            )

    if upper.startswith("INST OF ") or upper.startswith("INSTITUTE OF "):
        anchor = single_region_anchor(upper)
        if anchor:
            token, city, province = anchor
            return _geo_row(
                city,
                province,
                "university_location",
                f"Institute regional anchor '{token}'.",
                "institute region anchor",
            )

    return None
