from __future__ import annotations

import re

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, normalize_cn_text

PROVINCE_ZH_TO_EN = {
    "北京": "Beijing",
    "北京市": "Beijing",
    "上海": "Shanghai",
    "上海市": "Shanghai",
    "天津": "Tianjin",
    "天津市": "Tianjin",
    "重庆": "Chongqing",
    "重庆市": "Chongqing",
    "广东": "Guangdong",
    "广东省": "Guangdong",
    "江苏": "Jiangsu",
    "江苏省": "Jiangsu",
    "浙江": "Zhejiang",
    "浙江省": "Zhejiang",
    "山东": "Shandong",
    "山东省": "Shandong",
    "四川": "Sichuan",
    "四川省": "Sichuan",
    "湖北": "Hubei",
    "湖北省": "Hubei",
    "湖南": "Hunan",
    "湖南省": "Hunan",
    "河南": "Henan",
    "河南省": "Henan",
    "福建": "Fujian",
    "福建省": "Fujian",
    "安徽": "Anhui",
    "安徽省": "Anhui",
    "陕西": "Shaanxi",
    "陕西省": "Shaanxi",
    "辽宁": "Liaoning",
    "辽宁省": "Liaoning",
    "河北": "Hebei",
    "河北省": "Hebei",
    "江西": "Jiangxi",
    "江西省": "Jiangxi",
    "广西": "Guangxi",
    "广西壮族自治区": "Guangxi",
    "云南": "Yunnan",
    "云南省": "Yunnan",
    "贵州": "Guizhou",
    "贵州省": "Guizhou",
    "山西": "Shanxi",
    "山西省": "Shanxi",
    "吉林": "Jilin",
    "吉林省": "Jilin",
    "黑龙江": "Heilongjiang",
    "黑龙江省": "Heilongjiang",
    "内蒙古": "Inner Mongolia",
    "内蒙古自治区": "Inner Mongolia",
    "甘肃": "Gansu",
    "甘肃省": "Gansu",
    "新疆": "Xinjiang",
    "新疆维吾尔自治区": "Xinjiang",
    "海南": "Hainan",
    "海南省": "Hainan",
    "宁夏": "Ningxia",
    "宁夏回族自治区": "Ningxia",
    "青海": "Qinghai",
    "青海省": "Qinghai",
    "西藏": "Tibet",
    "西藏自治区": "Tibet",
}

CITY_SUFFIX_RE = re.compile(r"市$|地区$|盟$|州$")


def _known_city_lookup() -> dict[str, tuple[str, str]]:
    """Build city -> (city_en, province_en) from pilot zones and smart factories."""
    lookup: dict[str, tuple[str, str]] = {}
    for rel in (
        "data/processed/pilot_zones.csv",
        "data/processed/smart_factories_clean.csv",
    ):
        path = PROJECT_ROOT / rel
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            city = str(row.get("city", "")).strip()
            province = str(row.get("province", "")).strip()
            if city and province:
                lookup[normalize_cn_text(city)] = (city, province)
    return lookup


_KNOWN_CITIES = None


def known_city_lookup() -> dict[str, tuple[str, str]]:
    global _KNOWN_CITIES
    if _KNOWN_CITIES is None:
        _KNOWN_CITIES = _known_city_lookup()
    return _KNOWN_CITIES


def normalize_province(province: str | None) -> str:
    if province is None or (isinstance(province, float) and pd.isna(province)):
        return ""
    raw = str(province).strip()
    if not raw:
        return ""
    key = normalize_cn_text(raw)
    if key in PROVINCE_ZH_TO_EN:
        return PROVINCE_ZH_TO_EN[key]
    if raw in PROVINCE_ZH_TO_EN.values():
        return raw
    return raw.title() if raw.isascii() else raw


def normalize_city(
    city: str | None,
    province: str | None = None,
    address: str | None = None,
) -> tuple[str, str, str]:
    """Return (city_en, province_en, geocode_evidence)."""
    lookup = known_city_lookup()
    prov_en = normalize_province(province)

    for candidate in (city, address):
        if candidate is None or (isinstance(candidate, float) and pd.isna(candidate)):
            continue
        raw = str(candidate).strip()
        if not raw:
            continue
        key = normalize_cn_text(raw)
        if key in lookup:
            c, p = lookup[key]
            return c, p or prov_en, "known_city_registry"
        if raw in lookup.values():
            return raw, prov_en, "known_city_registry"
        m = re.search(r"([\u4e00-\u9fff]{2,12}市)", raw)
        if m:
            zh_city = m.group(1)
            zkey = normalize_cn_text(zh_city)
            if zkey in lookup:
                c, p = lookup[zkey]
                return c, p or prov_en, "address_city_token"
            city_en = zh_city[:-1] if zh_city.endswith("市") else zh_city
            return city_en, prov_en, "address_city_token_unmapped"

    if city is not None and not (isinstance(city, float) and pd.isna(city)):
        raw = str(city).strip()
        if raw:
            if raw.endswith("市"):
                return raw[:-1], prov_en, "city_field_zh"
            if raw.isascii():
                return raw.title(), prov_en, "city_field_en"
            return raw, prov_en, "city_field_raw"

    return "", prov_en, "missing"
