"""China prefecture-level city tokens for high-precision applicant-name geography."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CityEntry:
    city_en: str
    province_en: str
    zh_tokens: tuple[str, ...]
    en_tokens: tuple[str, ...]


# Municipality provinces use same name for city and province in Atlas contract.
MUNICIPALITIES = frozenset({"Beijing", "Shanghai", "Tianjin", "Chongqing", "Hong Kong", "Macau"})


def _entry(
    city_en: str,
    province_en: str,
    zh: tuple[str, ...],
    en: tuple[str, ...] = (),
) -> CityEntry:
  en_upper = tuple({city_en.upper().replace(" ", "")} | {e.upper().replace(" ", "") for e in en})
  return CityEntry(city_en=city_en, province_en=province_en, zh_tokens=zh, en_tokens=en_upper)


CITY_GAZETTEER: tuple[CityEntry, ...] = (
    _entry("Beijing", "Beijing", ("北京市", "北京"), ("BEIJING",)),
    _entry("Shanghai", "Shanghai", ("上海市", "上海"), ("SHANGHAI",)),
    _entry("Tianjin", "Tianjin", ("天津市", "天津"), ("TIANJIN",)),
    _entry("Chongqing", "Chongqing", ("重庆市", "重庆"), ("CHONGQING",)),
    _entry("Shenzhen", "Guangdong", ("深圳市", "深圳"), ("SHENZHEN",)),
    _entry("Guangzhou", "Guangdong", ("广州市", "广州"), ("GUANGZHOU", "CANTON")),
    _entry("Dongguan", "Guangdong", ("东莞市", "东莞"), ("DONGGUAN",)),
    _entry("Foshan", "Guangdong", ("佛山市", "佛山"), ("FOSHAN",)),
    _entry("Huizhou", "Guangdong", ("惠州市", "惠州"), ("HUIZHOU",)),
    _entry("Zhuhai", "Guangdong", ("珠海市", "珠海"), ("ZHUHAI",)),
    _entry("Zhongshan", "Guangdong", ("中山市", "中山"), ("ZHONGSHAN",)),
    _entry("Jiangmen", "Guangdong", ("江门市", "江门"), ("JIANGMEN",)),
    _entry("Hangzhou", "Zhejiang", ("杭州市", "杭州"), ("HANGZHOU",)),
    _entry("Ningbo", "Zhejiang", ("宁波市", "宁波"), ("NINGBO",)),
    _entry("Wenzhou", "Zhejiang", ("温州市", "温州"), ("WENZHOU",)),
    _entry("Jiaxing", "Zhejiang", ("嘉兴市", "嘉兴"), ("JIAXING",)),
    _entry("Huzhou", "Zhejiang", ("湖州市", "湖州"), ("HUZHOU",)),
    _entry("Shaoxing", "Zhejiang", ("绍兴市", "绍兴"), ("SHAOXING",)),
    _entry("Jinhua", "Zhejiang", ("金华市", "金华"), ("JINHUA",)),
    _entry("Taizhou", "Zhejiang", ("台州市", "台州"), ("TAIZHOU",)),
    _entry("Suzhou", "Jiangsu", ("苏州市", "苏州"), ("SUZHOU",)),
    _entry("Nanjing", "Jiangsu", ("南京市", "南京"), ("NANJING", "NANKING")),
    _entry("Wuxi", "Jiangsu", ("无锡市", "无锡"), ("WUXI",)),
    _entry("Changzhou", "Jiangsu", ("常州市", "常州"), ("CHANGZHOU",)),
    _entry("Nantong", "Jiangsu", ("南通市", "南通"), ("NANTONG",)),
    _entry("Xuzhou", "Jiangsu", ("徐州市", "徐州"), ("XUZHOU",)),
    _entry("Yangzhou", "Jiangsu", ("扬州市", "扬州"), ("YANGZHOU",)),
    _entry("Zhenjiang", "Jiangsu", ("镇江市", "镇江"), ("ZHENJIANG",)),
    _entry("Taizhou", "Jiangsu", ("泰州市", "泰州")),
    _entry("Wuhan", "Hubei", ("武汉市", "武汉"), ("WUHAN",)),
    _entry("Yichang", "Hubei", ("宜昌市", "宜昌"), ("YICHANG",)),
    _entry("Xiangyang", "Hubei", ("襄阳市", "襄阳", "襄樊市", "襄樊"), ("XIANGYANG",)),
    _entry("Chengdu", "Sichuan", ("成都市", "成都"), ("CHENGDU",)),
    _entry("Mianyang", "Sichuan", ("绵阳市", "绵阳"), ("MIANYANG",)),
    _entry("Deyang", "Sichuan", ("德阳市", "德阳"), ("DEYANG",)),
    _entry("Xi'an", "Shaanxi", ("西安市", "西安"), ("XIAN", "XIAN")),
    _entry("Hefei", "Anhui", ("合肥市", "合肥"), ("HEFEI",)),
    _entry("Wuhu", "Anhui", ("芜湖市", "芜湖"), ("WUHU",)),
    _entry("Bengbu", "Anhui", ("蚌埠市", "蚌埠"), ("BENGBU",)),
    _entry("Jinan", "Shandong", ("济南市", "济南"), ("JINAN",)),
    _entry("Qingdao", "Shandong", ("青岛市", "青岛"), ("QINGDAO", "TSINGTAO")),
    _entry("Yantai", "Shandong", ("烟台市", "烟台"), ("YANTAI",)),
    _entry("Weifang", "Shandong", ("潍坊市", "潍坊"), ("WEIFANG",)),
    _entry("Zibo", "Shandong", ("淄博市", "淄博"), ("ZIBO",)),
    _entry("Dalian", "Liaoning", ("大连市", "大连"), ("DALIAN",)),
    _entry("Shenyang", "Liaoning", ("沈阳市", "沈阳"), ("SHENYANG",)),
    _entry("Anshan", "Liaoning", ("鞍山市", "鞍山"), ("ANSHAN",)),
    _entry("Changchun", "Jilin", ("长春市", "长春"), ("CHANGCHUN",)),
    _entry("Harbin", "Heilongjiang", ("哈尔滨市", "哈尔滨"), ("HARBIN",)),
    _entry("Zhengzhou", "Henan", ("郑州市", "郑州"), ("ZHENGZHOU",)),
    _entry("Luoyang", "Henan", ("洛阳市", "洛阳"), ("LUOYANG",)),
    _entry("Changsha", "Hunan", ("长沙市", "长沙"), ("CHANGSHA",)),
    _entry("Zhuzhou", "Hunan", ("株洲市", "株洲"), ("ZHUZHOU",)),
    _entry("Fuzhou", "Fujian", ("福州市", "福州"), ("FUZHOU",)),
    _entry("Xiamen", "Fujian", ("厦门市", "厦门"), ("XIAMEN", "AMOY")),
    _entry("Quanzhou", "Fujian", ("泉州市", "泉州"), ("QUANZHOU",)),
    _entry("Nanchang", "Jiangxi", ("南昌市", "南昌"), ("NANCHANG",)),
    _entry("Kunming", "Yunnan", ("昆明市", "昆明"), ("KUNMING",)),
    _entry("Guiyang", "Guizhou", ("贵阳市", "贵阳"), ("GUIYANG",)),
    _entry("Nanning", "Guangxi", ("南宁市", "南宁"), ("NANNING",)),
    _entry("Liuzhou", "Guangxi", ("柳州市", "柳州"), ("LIUZHOU",)),
    _entry("Haikou", "Hainan", ("海口市", "海口"), ("HAIKOU",)),
    _entry("Sanya", "Hainan", ("三亚市", "三亚"), ("SANYA",)),
    _entry("Shijiazhuang", "Hebei", ("石家庄市", "石家庄"), ("SHIJIAZHUANG",)),
    _entry("Tangshan", "Hebei", ("唐山市", "唐山"), ("TANGSHAN",)),
    _entry("Baoding", "Hebei", ("保定市", "保定"), ("BAODING",)),
    _entry("Taiyuan", "Shanxi", ("太原市", "太原"), ("TAIYUAN",)),
    _entry("Hohhot", "Inner Mongolia", ("呼和浩特市", "呼和浩特"), ("HOHHOT",)),
    _entry("Urumqi", "Xinjiang", ("乌鲁木齐市", "乌鲁木齐"), ("URUMQI",)),
    _entry("Lanzhou", "Gansu", ("兰州市", "兰州"), ("LANZHOU",)),
    _entry("Yinchuan", "Ningxia", ("银川市", "银川"), ("YINCHUAN",)),
    _entry("Xining", "Qinghai", ("西宁市", "西宁"), ("XINING",)),
    _entry("Lhasa", "Tibet", ("拉萨市", "拉萨"), ("LHASA",)),
    _entry("Hong Kong", "Hong Kong", ("香港特别行政区", "香港"), ("HONGKONG", "HONG KONG")),
    _entry("Macau", "Macau", ("澳门特别行政区", "澳门"), ("MACAU", "MACAO")),
)

# Longest Chinese tokens first to prefer 深圳市 over 深圳 when both match same span.
_ZH_MATCHES: list[tuple[str, CityEntry]] = sorted(
    ((zh, entry) for entry in CITY_GAZETTEER for zh in entry.zh_tokens),
    key=lambda x: len(x[0]),
    reverse=True,
)

_EN_MATCHES: list[tuple[str, CityEntry]] = sorted(
    ((en, entry) for entry in CITY_GAZETTEER for en in entry.en_tokens if len(en) >= 4),
    key=lambda x: len(x[0]),
    reverse=True,
)

# Ambiguous short tokens — require word boundary / not used alone.
_AMBIGUOUS_ZH = frozenset({"朝阳", "通州", "和平", "长安", "城中", "城东"})


def first_applicant_name(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    return text.split(";")[0].split("|")[0].split(",")[0].strip()


def match_city_from_applicant_name(applicant_name: str) -> CityEntry | None:
    """Return city entry only on explicit token match; no fuzzy guess."""
    name = first_applicant_name(applicant_name)
    if not name:
        return None

    for zh, entry in _ZH_MATCHES:
        if zh in _AMBIGUOUS_ZH:
            continue
        if zh in name:
            return entry

    upper = re.sub(r"[^A-Z0-9]", "", name.upper())
    if not upper:
        return None

    for en, entry in _EN_MATCHES:
        if en in upper:
            return entry

    return None


def geography_from_applicant_name(applicant_name: str) -> dict[str, str]:
    """Contract row fields for name-token tier (blank if unresolved)."""
    entry = match_city_from_applicant_name(applicant_name)
    if entry is None:
        return {
            "applicant_city": "",
            "applicant_province": "",
            "applicant_address": "",
            "geo_source": "",
            "geo_match_confidence": "",
            "geo_notes": "",
        }

    city = entry.city_en
    province = entry.province_en
    address = f"{city}, {province}, CN (applicant_name city token)"
    return {
        "applicant_city": city,
        "applicant_province": province,
        "applicant_address": address,
        "geo_source": "IIDS applicant_name + China city gazetteer",
        "geo_match_confidence": "applicant_name_city_token",
        "geo_notes": f"Matched token in applicant_name: {first_applicant_name(applicant_name)[:120]}",
    }
