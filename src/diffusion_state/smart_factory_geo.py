from __future__ import annotations

import re
from dataclasses import dataclass

from diffusion_state.utils import PROJECT_ROOT, normalize_cn_text, read_yaml

CITY_IN_TEXT_RE = re.compile(r"([\u4e00-\u9fff]{2,12}市)")
PAREN_CITY_RE = re.compile(r"[（(]\s*([\u4e00-\u9fff]{2,10})\s*[）)]")

# Firm-name prefix -> (city_en, province_en); sourced from recurring list locations in MIIT tables.
FIRM_PREFIX_CITIES: list[tuple[str, str, str]] = [
    ("北京", "Beijing", "Beijing"),
    ("上海", "Shanghai", "Shanghai"),
    ("天津", "Tianjin", "Tianjin"),
    ("重庆", "Chongqing", "Chongqing"),
    ("武汉", "Wuhan", "Hubei"),
    ("南京", "Nanjing", "Jiangsu"),
    ("苏州", "Suzhou", "Jiangsu"),
    ("无锡", "Wuxi", "Jiangsu"),
    ("常州", "Changzhou", "Jiangsu"),
    ("南通", "Nantong", "Jiangsu"),
    ("杭州", "Hangzhou", "Zhejiang"),
    ("宁波", "Ningbo", "Zhejiang"),
    ("温州", "Wenzhou", "Zhejiang"),
    ("绍兴", "Shaoxing", "Zhejiang"),
    ("嘉兴", "Jiaxing", "Zhejiang"),
    ("湖州", "Huzhou", "Zhejiang"),
    ("广州", "Guangzhou", "Guangdong"),
    ("深圳", "Shenzhen", "Guangdong"),
    ("惠州", "Huizhou", "Guangdong"),
    ("珠海", "Zhuhai", "Guangdong"),
    ("佛山", "Foshan", "Guangdong"),
    ("东莞", "Dongguan", "Guangdong"),
    ("西安", "Xi'an", "Shaanxi"),
    ("成都", "Chengdu", "Sichuan"),
    ("沈阳", "Shenyang", "Liaoning"),
    ("大连", "Dalian", "Liaoning"),
    ("长春", "Changchun", "Jilin"),
    ("哈尔滨", "Harbin", "Heilongjiang"),
    ("青岛", "Qingdao", "Shandong"),
    ("济南", "Jinan", "Shandong"),
    ("烟台", "Yantai", "Shandong"),
    ("潍坊", "Weifang", "Shandong"),
    ("日照", "Rizhao", "Shandong"),
    ("淄博", "Zibo", "Shandong"),
    ("威海", "Weihai", "Shandong"),
    ("东营", "Dongying", "Shandong"),
    ("合肥", "Hefei", "Anhui"),
    ("芜湖", "Wuhu", "Anhui"),
    ("郑州", "Zhengzhou", "Henan"),
    ("洛阳", "Luoyang", "Henan"),
    ("长沙", "Changsha", "Hunan"),
    ("株洲", "Zhuzhou", "Hunan"),
    ("南昌", "Nanchang", "Jiangxi"),
    ("福州", "Fuzhou", "Fujian"),
    ("厦门", "Xiamen", "Fujian"),
    ("泉州", "Quanzhou", "Fujian"),
    ("昆明", "Kunming", "Yunnan"),
    ("贵阳", "Guiyang", "Guizhou"),
    ("兰州", "Lanzhou", "Gansu"),
    ("西宁", "Xining", "Qinghai"),
    ("银川", "Yinchuan", "Ningxia"),
    ("乌鲁木齐", "Urumqi", "Xinjiang"),
    ("唐山", "Tangshan", "Hebei"),
    ("保定", "Baoding", "Hebei"),
    ("廊坊", "Langfang", "Hebei"),
    ("石家庄", "Shijiazhuang", "Hebei"),
    ("太原", "Taiyuan", "Shanxi"),
    ("呼和浩特", "Hohhot", "Inner Mongolia"),
    ("包头", "Baotou", "Inner Mongolia"),
    ("鄂尔多斯", "Ordos", "Inner Mongolia"),
]


@dataclass(frozen=True)
class GeoResult:
    province: str
    city: str
    city_confidence: str
    geo_notes: str


def normalize_firm_name_zh(name: str) -> str:
    """Collapse whitespace variants present in source HTML (e.g. '（ 宁波）')."""
    n = normalize_cn_text(name)
    n = re.sub(r"[（(]\s*", "（", n)
    n = re.sub(r"\s*[）)]", "）", n)
    return n


def _load_geo_config() -> dict:
    return read_yaml(PROJECT_ROOT / "configs" / "province_normalization.yml")


def _city_from_firm_province_county(firm_name_zh: str) -> GeoResult | None:
    """e.g. 福建省晋江市 -> Jinjiang, Fujian."""
    m = re.search(r"([\u4e00-\u9fff]{2,5}省)([\u4e00-\u9fff]{2,8}市)", firm_name_zh)
    if not m:
        return None
    prov_zh, city_zh = m.group(1), m.group(2)
    cfg = _load_geo_config()
    prov = cfg.get("provinces", {}).get(prov_zh)
    city = _prefecture_city_en(city_zh)
    if prov and city:
        return GeoResult(prov, city, "high", f"city from firm text: {prov_zh}{city_zh}")
    return None


def _city_from_location_string(location_raw: str, cfg: dict) -> GeoResult:
    loc = (location_raw or "").strip().replace("\xa0", "")
    if not loc:
        return GeoResult("unknown", "unknown", "unknown", "missing location")

    municipalities = cfg.get("municipalities", {})
    if loc in municipalities:
        entry = municipalities[loc]
        return GeoResult(
            entry["province"],
            entry["city"],
            "exact",
            f"location field is direct municipality: {loc}",
        )

    provinces = cfg.get("provinces", {})
    if loc in provinces:
        return GeoResult(
            provinces[loc],
            "unknown",
            "unknown",
            f"location is province-only: {loc}",
        )

    if loc.endswith("市") and loc not in provinces:
        city_en = _prefecture_city_en(loc)
        province_en = _province_for_prefecture_city(loc)
        if city_en and province_en:
            return GeoResult(
                province_en,
                city_en,
                "exact",
                f"location is prefecture-level city: {loc}",
            )

    return GeoResult("unknown", "unknown", "unknown", f"unparsed location: {loc}")


def _prefecture_city_en(loc: str) -> str | None:
    mapping = {
        "深圳市": "Shenzhen",
        "广州市": "Guangzhou",
        "武汉市": "Wuhan",
        "南京市": "Nanjing",
        "苏州市": "Suzhou",
        "杭州市": "Hangzhou",
        "宁波市": "Ningbo",
        "青岛市": "Qingdao",
        "大连市": "Dalian",
        "厦门市": "Xiamen",
        "西安市": "Xi'an",
        "成都市": "Chengdu",
        "长沙市": "Changsha",
        "郑州市": "Zhengzhou",
        "沈阳市": "Shenyang",
        "惠州市": "Huizhou",
        "珠海市": "Zhuhai",
        "合肥市": "Hefei",
        "无锡市": "Wuxi",
        "常州市": "Changzhou",
        "南通市": "Nantong",
        "潍坊市": "Weifang",
        "烟台市": "Yantai",
        "日照市": "Rizhao",
        "唐山市": "Tangshan",
        "保定市": "Baoding",
        "廊坊市": "Langfang",
        "鄂尔多斯市": "Ordos",
        "包头市": "Baotou",
        "银川市": "Yinchuan",
        "乌鲁木齐市": "Urumqi",
        "西宁市": "Xining",
        "兰州市": "Lanzhou",
        "昆明市": "Kunming",
        "贵阳市": "Guiyang",
        "南昌市": "Nanchang",
        "福州市": "Fuzhou",
        "泉州市": "Quanzhou",
        "温州市": "Wenzhou",
        "绍兴市": "Shaoxing",
        "嘉兴市": "Jiaxing",
        "湖州市": "Huzhou",
        "德州市": "Dezhou",
        "济宁市": "Jining",
        "淄博市": "Zibo",
        "威海市": "Weihai",
        "东营市": "Dongying",
        "芜湖市": "Wuhu",
        "蚌埠市": "Bengbu",
        "洛阳市": "Luoyang",
        "襄阳市": "Xiangyang",
        "株洲市": "Zhuzhou",
        "柳州市": "Liuzhou",
        "海口市": "Haikou",
        "三亚市": "Sanya",
        "晋江市": "Jinjiang",
        "漳州市": "Zhangzhou",
        "湘潭市": "Xiangtan",
        "吴忠市": "Wuzhong",
        "文山市": "Wenshan",
    }
    return mapping.get(loc)


def _province_for_prefecture_city(loc: str) -> str | None:
    city_province = {
        "深圳市": "Guangdong",
        "广州市": "Guangdong",
        "武汉市": "Hubei",
        "南京市": "Jiangsu",
        "苏州市": "Jiangsu",
        "无锡市": "Jiangsu",
        "常州市": "Jiangsu",
        "南通市": "Jiangsu",
        "杭州市": "Zhejiang",
        "宁波市": "Zhejiang",
        "温州市": "Zhejiang",
        "绍兴市": "Zhejiang",
        "嘉兴市": "Zhejiang",
        "湖州市": "Zhejiang",
        "惠州市": "Guangdong",
        "珠海市": "Guangdong",
        "厦门市": "Fujian",
        "福州市": "Fujian",
        "泉州市": "Fujian",
        "青岛市": "Shandong",
        "烟台市": "Shandong",
        "潍坊市": "Shandong",
        "日照市": "Shandong",
        "淄博市": "Shandong",
        "威海市": "Shandong",
        "东营市": "Shandong",
        "德州市": "Shandong",
        "济宁市": "Shandong",
        "西安市": "Shaanxi",
        "成都市": "Sichuan",
        "长沙市": "Hunan",
        "株洲市": "Hunan",
        "郑州市": "Henan",
        "洛阳市": "Henan",
        "沈阳市": "Liaoning",
        "大连市": "Liaoning",
        "唐山市": "Hebei",
        "保定市": "Hebei",
        "廊坊市": "Hebei",
        "合肥市": "Anhui",
        "芜湖市": "Anhui",
        "蚌埠市": "Anhui",
        "南昌市": "Jiangxi",
        "昆明市": "Yunnan",
        "贵阳市": "Guizhou",
        "兰州市": "Gansu",
        "西宁市": "Qinghai",
        "银川市": "Ningxia",
        "乌鲁木齐市": "Xinjiang",
        "鄂尔多斯市": "Inner Mongolia",
        "包头市": "Inner Mongolia",
        "海口市": "Hainan",
        "三亚市": "Hainan",
        "柳州市": "Guangxi",
        "襄阳市": "Hubei",
        "晋江市": "Fujian",
        "漳州市": "Fujian",
        "湘潭市": "Hunan",
        "吴忠市": "Ningxia",
        "文山市": "Yunnan",
    }
    return city_province.get(loc)


def _city_from_firm_parenthetical(firm_name_zh: str) -> GeoResult | None:
    m = PAREN_CITY_RE.search(firm_name_zh)
    if not m:
        return None
    cn = m.group(1)
    for prefix, city_en, province_en in FIRM_PREFIX_CITIES:
        if cn == prefix or cn == prefix + "市":
            return GeoResult(
                province_en,
                city_en,
                "high",
                f"city from parenthetical in firm name: {cn}",
            )
    return None


def _city_from_firm_prefix(firm_name_zh: str) -> GeoResult | None:
    firm = normalize_cn_text(firm_name_zh)
    for prefix, city_en, province_en in sorted(
        FIRM_PREFIX_CITIES, key=lambda x: len(x[0]), reverse=True
    ):
        if firm.startswith(prefix):
            return GeoResult(
                province_en,
                city_en,
                "high",
                f"city from firm-name prefix: {prefix}",
            )
    return None


def suggest_city_from_source_text(
    location_raw: str,
    firm_name_zh: str,
    project_name_zh: str,
) -> dict[str, str]:
    """Non-mutating hint for manual review queue; does not assign city to clean rows."""
    firm_name_zh = normalize_firm_name_zh(firm_name_zh)
    cfg = _load_geo_config()
    candidates: list[tuple[str, str, str, str]] = []

    def _add(hit: GeoResult | None, evidence_type: str, source_label: str) -> None:
        if hit and hit.city != "unknown":
            candidates.append((hit.city, hit.province, hit.city_confidence, f"{evidence_type}: {source_label}"))

    _add(_city_from_location_string(location_raw, cfg), "miit_location_field", location_raw or "")
    _add(_city_from_firm_province_county(firm_name_zh), "firm_text", firm_name_zh)
    _add(_city_from_firm_parenthetical(firm_name_zh), "firm_parenthetical", firm_name_zh)
    _add(_city_from_firm_prefix(firm_name_zh), "firm_prefix", firm_name_zh)

    for match in CITY_IN_TEXT_RE.findall(project_name_zh or ""):
        if match in {"中国市", "本市"}:
            continue
        city = _prefecture_city_en(match)
        if city:
            prov = _province_for_prefecture_city(match) or "unknown"
            candidates.append((city, prov, "high", f"project_name: {match}"))

    if not candidates:
        return {
            "candidate_city": "",
            "candidate_evidence_type": "",
            "confidence": "",
            "notes": "",
        }

    city, prov, conf, note = candidates[0]
    return {
        "candidate_city": city,
        "candidate_evidence_type": note.split(":")[0],
        "confidence": conf,
        "notes": f"Parser hint only — verify before override. {note}",
    }


def resolve_geo(location_raw: str, firm_name_zh: str, project_name_zh: str) -> GeoResult:
    firm_name_zh = normalize_firm_name_zh(firm_name_zh)
    cfg = _load_geo_config()
    base = _city_from_location_string(location_raw, cfg)
    if base.city != "unknown":
        return base

    for infer in (
        lambda: _city_from_firm_province_county(firm_name_zh),
        lambda: _city_from_firm_parenthetical(firm_name_zh),
        lambda: _city_from_firm_prefix(firm_name_zh),
    ):
        hit = infer()
        if hit:
            if base.province != "unknown" and hit.province == "unknown":
                return GeoResult(base.province, hit.city, hit.city_confidence, hit.geo_notes)
            return hit

    for source, label in (
        (project_name_zh, "project name"),
        (firm_name_zh, "firm name"),
    ):
        for match in CITY_IN_TEXT_RE.findall(source or ""):
            if match in {"中国市", "本市"}:
                continue
            city = _prefecture_city_en(match)
            if not city:
                continue
            prov = _province_for_prefecture_city(match) or base.province
            return GeoResult(
                prov if prov != "unknown" else "unknown",
                city,
                "high",
                f"city inferred from {label}: {match}",
            )

    if base.province != "unknown":
        return base
    return GeoResult("unknown", "unknown", "unknown", base.geo_notes)
