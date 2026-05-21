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


def _load_geo_tokens() -> list[tuple[str, str, str]]:
    cfg = read_yaml(PROJECT_ROOT / "configs" / "city_geo_tokens.yml")
    rows = []
    for entry in cfg.get("tokens", []):
        rows.append((entry["zh"], entry["city"], entry["province"]))
    return sorted(rows, key=lambda x: len(x[0]), reverse=True)


def _load_locality_aliases() -> dict[str, dict[str, str]]:
    path = PROJECT_ROOT / "configs" / "city_locality_aliases.yml"
    if not path.exists():
        return {}
    return read_yaml(path).get("aliases", {})


def resolve_cn_locality(cn: str) -> tuple[str, str] | None:
    """Map a Chinese place name (with or without 市) to (city_en, province_en)."""
    cn = normalize_cn_text(cn).strip()
    if not cn:
        return None
    if cn.endswith("市"):
        cn = cn[:-1]

    alias = _load_locality_aliases().get(cn)
    if alias:
        return alias["city"], alias["province"]

    for zh, city_en, prov_en in _load_geo_tokens():
        if cn == zh or cn.startswith(zh):
            return city_en, prov_en

    for prefix, city_en, province_en in FIRM_PREFIX_CITIES:
        if cn == prefix:
            return city_en, province_en

    city_en = _prefecture_city_en(f"{cn}市")
    prov_en = _province_for_prefecture_city(f"{cn}市")
    if city_en and prov_en:
        return city_en, prov_en
    return None


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
        "淮安市": "Huai'an",
        "九江市": "Jiujiang",
        "盐城市": "Yancheng",
        "泰州市": "Taizhou",
        "镇江市": "Zhenjiang",
        "连云港市": "Lianyungang",
        "扬州市": "Yangzhou",
        "徐州市": "Xuzhou",
        "南通市": "Nantong",
        "宿迁市": "Suqian",
        "丽水市": "Lishui",
        "金华市": "Jinhua",
        "衢州市": "Quzhou",
        "舟山市": "Zhoushan",
        "台州市": "Taizhou",
        "茂名市": "Maoming",
        "湛江市": "Zhanjiang",
        "江门市": "Jiangmen",
        "中山市": "Zhongshan",
        "东莞市": "Dongguan",
        "佛山市": "Foshan",
        "济南市": "Jinan",
        "临沂市": "Linyi",
        "济宁市": "Jining",
        "泰安市": "Tai'an",
        "聊城市": "Liaocheng",
        "滨州市": "Binzhou",
        "菏泽市": "Heze",
        "枣庄市": "Zaozhuang",
        "绵阳市": "Mianyang",
        "德阳市": "Deyang",
        "乐山市": "Leshan",
        "泸州市": "Luzhou",
        "宜宾市": "Yibin",
        "达州市": "Dazhou",
        "自贡市": "Zigong",
        "攀枝花市": "Panzhihua",
        "桂林市": "Guilin",
        "钦州市": "Qinzhou",
        "防城港市": "Fangchenggang",
        "北海市": "Beihai",
        "百色市": "Baise",
        "黄石市": "Huangshi",
        "宜昌市": "Yichang",
        "荆州市": "Jingzhou",
        "襄阳市": "Xiangyang",
        "十堰市": "Shiyan",
        "赣州市": "Ganzhou",
        "吉安市": "Ji'an",
        "九江市": "Jiujiang",
        "上饶市": "Shangrao",
        "景德镇市": "Jingdezhen",
        "鹰潭市": "Yingtan",
        "新余市": "Xinyu",
        "贵溪市": "Guixi",
        "鞍山市": "Anshan",
        "本溪市": "Benxi",
        "抚顺市": "Fushun",
        "锦州市": "Jinzhou",
        "营口市": "Yingkou",
        "盘锦市": "Panjin",
        "铁岭市": "Tieling",
        "朝阳市": "Chaoyang",
        "葫芦岛市": "Huludao",
        "齐齐哈尔市": "Qiqihar",
        "大庆市": "Daqing",
        "克拉玛依市": "Karamay",
        "石嘴山市": "Shizuishan",
        "中卫市": "Zhongwei",
        "固原市": "Guyuan",
        "吴忠市": "Wuzhong",
        "铜川市": "Tongchuan",
        "宝鸡市": "Baoji",
        "咸阳市": "Xianyang",
        "渭南市": "Weinan",
        "汉中市": "Hanzhong",
        "榆林市": "Yulin",
        "延安市": "Yan'an",
        "拉萨市": "Lhasa",
        "库尔勒市": "Korla",
        "阿克苏市": "Aksu",
        "石河子市": "Shihezi",
        "昌吉市": "Changji",
        "独山子区": "Karamay",
        "秦皇岛市": "Qinhuangdao",
        "邯郸市": "Handan",
        "邢台市": "Xingtai",
        "沧州市": "Cangzhou",
        "衡水市": "Hengshui",
        "承德市": "Chengde",
        "张家口市": "Zhangjiakou",
        "大同市": "Datong",
        "长治市": "Changzhi",
        "晋城市": "Jincheng",
        "临汾市": "Linfen",
        "运城市": "Yuncheng",
        "呼和浩特市": "Hohhot",
        "包头市": "Baotou",
        "乌海市": "Wuhai",
        "赤峰市": "Chifeng",
        "通辽市": "Tongliao",
        "鄂尔多斯市": "Ordos",
        "锡林浩特市": "Xilinhot",
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
        "淮安市": "Jiangsu",
        "九江市": "Jiangxi",
        "盐城市": "Jiangsu",
        "泰州市": "Jiangsu",
        "镇江市": "Jiangsu",
        "连云港市": "Jiangsu",
        "扬州市": "Jiangsu",
        "徐州市": "Jiangsu",
        "宿迁市": "Jiangsu",
        "茂名市": "Guangdong",
        "湛江市": "Guangdong",
        "江门市": "Guangdong",
        "中山市": "Guangdong",
        "东莞市": "Guangdong",
        "佛山市": "Guangdong",
        "济南市": "Shandong",
        "临沂市": "Shandong",
        "济宁市": "Shandong",
        "泰安市": "Shandong",
        "聊城市": "Shandong",
        "滨州市": "Shandong",
        "菏泽市": "Shandong",
        "枣庄市": "Shandong",
        "绵阳市": "Sichuan",
        "德阳市": "Sichuan",
        "乐山市": "Sichuan",
        "泸州市": "Sichuan",
        "宜宾市": "Sichuan",
        "达州市": "Sichuan",
        "自贡市": "Sichuan",
        "攀枝花市": "Sichuan",
        "桂林市": "Guangxi",
        "钦州市": "Guangxi",
        "防城港市": "Guangxi",
        "北海市": "Guangxi",
        "百色市": "Guangxi",
        "黄石市": "Hubei",
        "宜昌市": "Hubei",
        "荆州市": "Hubei",
        "襄阳市": "Hubei",
        "十堰市": "Hubei",
        "赣州市": "Jiangxi",
        "吉安市": "Jiangxi",
        "上饶市": "Jiangxi",
        "景德镇市": "Jiangxi",
        "鹰潭市": "Jiangxi",
        "新余市": "Jiangxi",
        "贵溪市": "Jiangxi",
        "鞍山市": "Liaoning",
        "本溪市": "Liaoning",
        "抚顺市": "Liaoning",
        "锦州市": "Liaoning",
        "营口市": "Liaoning",
        "盘锦市": "Liaoning",
        "铁岭市": "Liaoning",
        "朝阳市": "Liaoning",
        "葫芦岛市": "Liaoning",
        "齐齐哈尔市": "Heilongjiang",
        "大庆市": "Heilongjiang",
        "克拉玛依市": "Xinjiang",
        "石嘴山市": "Ningxia",
        "中卫市": "Ningxia",
        "固原市": "Ningxia",
        "铜川市": "Shaanxi",
        "宝鸡市": "Shaanxi",
        "咸阳市": "Shaanxi",
        "渭南市": "Shaanxi",
        "汉中市": "Shaanxi",
        "榆林市": "Shaanxi",
        "延安市": "Shaanxi",
        "拉萨市": "Tibet",
        "库尔勒市": "Xinjiang",
        "阿克苏市": "Xinjiang",
        "石河子市": "Xinjiang",
        "昌吉市": "Xinjiang",
        "秦皇岛市": "Hebei",
        "邯郸市": "Hebei",
        "邢台市": "Hebei",
        "沧州市": "Hebei",
        "衡水市": "Hebei",
        "承德市": "Hebei",
        "张家口市": "Hebei",
        "大同市": "Shanxi",
        "长治市": "Shanxi",
        "晋城市": "Shanxi",
        "临汾市": "Shanxi",
        "运城市": "Shanxi",
        "呼和浩特市": "Inner Mongolia",
        "乌海市": "Inner Mongolia",
        "赤峰市": "Inner Mongolia",
        "通辽市": "Inner Mongolia",
        "锡林浩特市": "Inner Mongolia",
    }
    return city_province.get(loc)


def _city_from_firm_parenthetical(firm_name_zh: str) -> GeoResult | None:
    m = PAREN_CITY_RE.search(firm_name_zh)
    if not m:
        return None
    cn = m.group(1)
    hit = resolve_cn_locality(cn)
    if hit:
        city_en, province_en = hit
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

    from diffusion_state.audited_city_resolution import infer_audited_resolution

    prov_hint = base.province if base.province != "unknown" else "unknown"
    audited = infer_audited_resolution(
        location_raw=location_raw,
        firm_name_zh=firm_name_zh,
        project_name_zh=project_name_zh,
        province=prov_hint,
        source_url="",
    )
    if audited and audited.city_confidence in {"exact", "high"}:
        return GeoResult(
            audited.province,
            audited.city,
            audited.city_confidence,
            audited.notes,
        )

    if base.province != "unknown":
        return base

    return GeoResult("unknown", "unknown", "unknown", base.geo_notes)
