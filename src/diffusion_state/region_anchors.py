"""Shared province/region token -> (city, province) anchors for English IIDS applicant names."""
from __future__ import annotations

# Longest tokens first when matching via substring search.
REGION_ANCHORS: tuple[tuple[str, str, str], ...] = tuple(
    sorted(
        [
            ("INNER MONGOLIA", "Hohhot", "Inner Mongolia"),
            ("HEILONGJIANG", "Harbin", "Heilongjiang"),
            ("ELECTRONIC SCIENCE & TECH CHINA", "Chengdu", "Sichuan"),
            ("ELECTRONIC SCI & TECH CHINA", "Chengdu", "Sichuan"),
            ("ELECTRONIC SCIENCE & TECH", "Chengdu", "Sichuan"),
            ("ELECTRONIC SCI & TECH", "Chengdu", "Sichuan"),
            ("NORTHWESTERN POLYTECHNICAL", "Xi'an", "Shaanxi"),
            ("NORTHEAST FORESTRY", "Harbin", "Heilongjiang"),
            ("SOUTH CHINA TECH", "Guangzhou", "Guangdong"),
            ("SOUTH CHINA NORMAL", "Guangzhou", "Guangdong"),
            ("SOUTH CHINA AGRICULT", "Guangzhou", "Guangdong"),
            ("SOUTHERN SCI & TECH", "Shenzhen", "Guangdong"),
            ("NORTH CHINA ELECTRIC POWER", "Beijing", "Beijing"),
            ("NORTH CHINA WATER RESOURCES", "Zhengzhou", "Henan"),
            ("EAST CHINA NORMAL", "Shanghai", "Shanghai"),
            ("EAST CHINA SCIENCE & TECH", "Shanghai", "Shanghai"),
            ("EAST CHINA", "Shanghai", "Shanghai"),
            ("CHINA AGRICULTURAL", "Beijing", "Beijing"),
            ("CHINA PETROLEUM", "Beijing", "Beijing"),
            ("CHINA MEDICAL", "Shenyang", "Liaoning"),
            ("OCEAN CHINA", "Qingdao", "Shandong"),
            ("MINZU CHINA", "Beijing", "Beijing"),
            ("HUAZHONG AGRICULTURAL", "Wuhan", "Hubei"),
            ("CAPITAL NORMAL", "Beijing", "Beijing"),
            ("CIVIL AVIATION CHINA", "Tianjin", "Tianjin"),
            ("GUANGDONG", "Guangzhou", "Guangdong"),
            ("ZHEJIANG", "Hangzhou", "Zhejiang"),
            ("JIANGSU", "Nanjing", "Jiangsu"),
            ("SHANDONG", "Jinan", "Shandong"),
            ("SICHUAN", "Chengdu", "Sichuan"),
            ("SHAANXI", "Xi'an", "Shaanxi"),
            ("HEBEI", "Shijiazhuang", "Hebei"),
            ("HENAN", "Zhengzhou", "Henan"),
            ("HUBEI", "Wuhan", "Hubei"),
            ("HUNAN", "Changsha", "Hunan"),
            ("ANHUI", "Hefei", "Anhui"),
            ("FUJIAN", "Fuzhou", "Fujian"),
            ("JIANGXI", "Nanchang", "Jiangxi"),
            ("YUNNAN", "Kunming", "Yunnan"),
            ("GUIZHOU", "Guiyang", "Guizhou"),
            ("GANSU", "Lanzhou", "Gansu"),
            ("QINGHAI", "Xining", "Qinghai"),
            ("NINGXIA", "Yinchuan", "Ningxia"),
            ("XINJIANG", "Urumqi", "Xinjiang"),
            ("TIBET", "Lhasa", "Tibet"),
            ("HAINAN", "Haikou", "Hainan"),
            ("LIAONING", "Shenyang", "Liaoning"),
            ("JILIN", "Changchun", "Jilin"),
            ("SHANXI", "Taiyuan", "Shanxi"),
            ("GUANGXI", "Nanning", "Guangxi"),
            ("GUILIN", "Guilin", "Guangxi"),
            ("DALIAN", "Dalian", "Liaoning"),
            ("QINGDAO", "Qingdao", "Shandong"),
            ("SHENZHEN", "Shenzhen", "Guangdong"),
            ("WUHAN", "Wuhan", "Hubei"),
            ("NANJING", "Nanjing", "Jiangsu"),
            ("HANGZHOU", "Hangzhou", "Zhejiang"),
            ("SUZHOU", "Suzhou", "Jiangsu"),
            ("WUXI", "Wuxi", "Jiangsu"),
            ("NINGBO", "Ningbo", "Zhejiang"),
            ("YANGTZE", "Jingzhou", "Hubei"),
            ("WUYI", "Jiangmen", "Guangdong"),
            ("XIAN", "Xi'an", "Shaanxi"),
            ("BEIJING", "Beijing", "Beijing"),
            ("SHANGHAI", "Shanghai", "Shanghai"),
            ("TIANJIN", "Tianjin", "Tianjin"),
            ("CHONGQING", "Chongqing", "Chongqing"),
            ("PEKING", "Beijing", "Beijing"),
            ("TSINGHUA", "Beijing", "Beijing"),
            ("NANKAI", "Tianjin", "Tianjin"),
            ("TONGJI", "Shanghai", "Shanghai"),
            ("JIAOTONG", "Shanghai", "Shanghai"),
            ("HARBIN", "Harbin", "Heilongjiang"),
            ("USTC", "Hefei", "Anhui"),
            ("SOOCHOW", "Suzhou", "Jiangsu"),
            ("HUAIAN", "Huai'an", "Jiangsu"),
            ("YANCHENG", "Yancheng", "Jiangsu"),
            ("KUNSHAN", "Kunshan", "Jiangsu"),
            ("ZHONGSHAN", "Zhongshan", "Guangdong"),
            ("DONGGUAN", "Dongguan", "Guangdong"),
            ("FOSHAN", "Foshan", "Guangdong"),
            ("ZHUHAI", "Zhuhai", "Guangdong"),
            ("XIAMEN", "Xiamen", "Fujian"),
            ("NANCHANG", "Nanchang", "Jiangxi"),
            ("LANZHOU", "Lanzhou", "Gansu"),
        ],
        key=lambda x: len(x[0]),
        reverse=True,
    )
)


def region_anchor_hits(upper_name: str) -> list[tuple[str, str, str]]:
    """Return all (token, city, province) anchors present in upper_name."""
    hits: list[tuple[str, str, str]] = []
    for token, city, province in REGION_ANCHORS:
        if city and token in upper_name:
            hits.append((token, city, province))
    return hits


def single_region_anchor(upper_name: str) -> tuple[str, str, str] | None:
    hits = region_anchor_hits(upper_name)
    if not hits:
        return None
    # Keep only maximal (longest) tokens — avoids double-counting nested anchors.
    maximal = [
        h
        for h in hits
        if not any(len(h[0]) < len(o[0]) and h[0] in o[0] for o in hits if o is not h)
    ]
    if len(maximal) != 1:
        return None
    return maximal[0]
