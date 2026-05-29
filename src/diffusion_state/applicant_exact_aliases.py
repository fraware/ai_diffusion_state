"""Exact first-applicant_name -> HQ city mappings for high-volume English IIDS variants."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from diffusion_state.china_city_gazetteer import first_applicant_name

_GENERATED_REGISTRY = (
    Path(__file__).resolve().parents[2] / "data/seed/p12_region_anchor_aliases.json"
)

# name -> (city, province, confidence, notes)
_EXACT_ALIASES: dict[str, tuple[str, str, str, str]] = {
    "SUN YAT-SEN UNIV": (
        "Guangzhou",
        "Guangdong",
        "university_location",
        "Sun Yat-sen University.",
    ),
    "CHANG'AN UNIV": ("Xi'an", "Shaanxi", "university_location", "Chang'an University."),
    "CHANGAN UNIV": ("Xi'an", "Shaanxi", "university_location", "Chang'an University."),
    "NARI TECHNOLOGY CO LTD": (
        "Nanjing",
        "Jiangsu",
        "official_headquarters_page",
        "NARI Technology (State Grid affiliate).",
    ),
    "CHINA SOUTHERN POWER GRID CO LTD": (
        "Guangzhou",
        "Guangdong",
        "official_headquarters_page",
        "China Southern Power Grid.",
    ),
    "CHINA NAT PETROLEUM CORP": (
        "Beijing",
        "Beijing",
        "official_headquarters_page",
        "CNPC.",
    ),
    "CHINESE RES ACAD ENV SCIENCES": (
        "Beijing",
        "Beijing",
        "university_location",
        "Chinese Research Academy of Environmental Sciences.",
    ),
    "CHINA INST ATOMIC ENERGY": (
        "Beijing",
        "Beijing",
        "university_location",
        "China Institute of Atomic Energy.",
    ),
    "CHINA FAW GROUP CORP": (
        "Changchun",
        "Jilin",
        "official_headquarters_page",
        "FAW Group.",
    ),
    "EAST CHINA INST TECHNOLOGY": (
        "Nanjing",
        "Jiangsu",
        "university_location",
        "East China Institute of Technology.",
    ),
    "HUAIYIN INST TECHNOLOGY": (
        "Huai'an",
        "Jiangsu",
        "university_location",
        "Huaiyin Institute of Technology.",
    ),
    "YANCHENG INST TECH": (
        "Yancheng",
        "Jiangsu",
        "university_location",
        "Yancheng Institute of Technology.",
    ),
    "GLOBAL ENERGY INTERCONNECTION RES INST CO LTD": (
        "Beijing",
        "Beijing",
        "official_headquarters_page",
        "Global Energy Interconnection Research Institute.",
    ),
    "UNIV SOUTHERN SCI & TECH": (
        "Shenzhen",
        "Guangdong",
        "university_location",
        "Southern University of Science and Technology.",
    ),
    "UNIV SW SCI & TECH SWUST": (
        "Mianyang",
        "Sichuan",
        "university_location",
        "Southwest University of Science and Technology.",
    ),
    "UNIV NORTH CHINA TECHNOLOGY": (
        "Taiyuan",
        "Shanxi",
        "university_location",
        "North China University of Technology.",
    ),
    "UNIV NORTHWEST NORMAL": (
        "Lanzhou",
        "Gansu",
        "university_location",
        "Northwest Normal University.",
    ),
    "UNIV SHANDONG JIAOTONG": (
        "Jinan",
        "Shandong",
        "university_location",
        "Shandong Jiaotong University.",
    ),
    "UNIV CIVIL AVIATION CHINA": (
        "Tianjin",
        "Tianjin",
        "university_location",
        "Civil Aviation University of China.",
    ),
    "UNIV CAPITAL NORMAL": (
        "Beijing",
        "Beijing",
        "university_location",
        "Capital Normal University.",
    ),
    "UNIV WUYI": (
        "Jiangmen",
        "Guangdong",
        "university_location",
        "Wuyi University (Jiangmen).",
    ),
    "UNIV YANGTZE": (
        "Jingzhou",
        "Hubei",
        "university_location",
        "Yangtze University.",
    ),
    "UNIV XIHUA": (
        "Chengdu",
        "Sichuan",
        "university_location",
        "Xihua University.",
    ),
    "UNIV HUAZHONG AGRICULTURAL": (
        "Wuhan",
        "Hubei",
        "university_location",
        "Huazhong Agricultural University.",
    ),
    "UNIV ELECTRONIC SCIENCE & TECH": (
        "Chengdu",
        "Sichuan",
        "university_location",
        "UESTC (English export variant).",
    ),
    "WEST CHINA HOSPITAL SICHUAN UNIV": (
        "Chengdu",
        "Sichuan",
        "university_location",
        "West China Hospital, Sichuan University.",
    ),
    "YUNGU GUAN TECH CO LTD": (
        "Guiyang",
        "Guizhou",
        "official_headquarters_page",
        "Yungu Guan Technology.",
    ),
}


@lru_cache(maxsize=1)
def _generated_aliases() -> dict[str, tuple[str, str, str, str]]:
    if not _GENERATED_REGISTRY.exists():
        return {}
    raw = json.loads(_GENERATED_REGISTRY.read_text(encoding="utf-8"))
    out: dict[str, tuple[str, str, str, str]] = {}
    for name, row in raw.items():
        out[name] = (
            str(row.get("applicant_city") or ""),
            str(row.get("applicant_province") or ""),
            str(row.get("geo_match_confidence") or "official_headquarters_page"),
            str(row.get("geo_notes") or ""),
        )
    return out


def geography_from_exact_alias(applicant_name: str) -> dict[str, str] | None:
    first = first_applicant_name(applicant_name)
    if not first:
        return None
    loc = _EXACT_ALIASES.get(first) or _generated_aliases().get(first)
    if not loc:
        return None
    city, province, conf, notes = loc
    if not city:
        return None
    return {
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": f"{city}, {province}, CN (exact applicant alias)",
        "geo_source": "IIDS applicant_name + exact alias registry",
        "geo_match_confidence": conf,
        "geo_notes": notes,
    }
