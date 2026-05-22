"""Normalize ChinaUTC China City Statistical Yearbook downloads into repo city controls.

Input directory created by scripts/24_fetch_chinautc_city_yearbook.py:

    data/raw/city_controls/chinautc_downloads/

Output:

    data/raw/city_controls/chinautc_city_controls_public_fallback.csv
    data/raw/city_controls/chinautc_city_controls_public_fallback_missingness.csv

Important: this is a public fallback, not an EPS substitute. It parses whatever city-level
XLSX tables are available locally and fills missing contract variables with NaN. If the
full RAR files are extracted into the same year folders, the parser will attempt to use
additional tables by filename keywords.

The script is deliberately conservative. It will not manufacture FDI, fixed investment,
education, telecom, foreign trade, or industrial output if those tables are not present.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "city_controls"
DL = RAW / "chinautc_downloads"
OUT = RAW / "chinautc_city_controls_public_fallback.csv"
MISS = RAW / "chinautc_city_controls_public_fallback_missingness.csv"

REQUIRED = [
    "city",
    "province",
    "year",
    "gdp",
    "gdp_per_capita",
    "secondary_value_added",
    "industrial_output",
    "population",
    "employment",
    "average_wage",
    "fdi",
    "fixed_asset_investment",
    "education_proxy",
    "telecom_or_internet_proxy",
    "foreign_trade",
    "source_name",
    "source_file",
]

# Chinese city/county/prefecture tokens observed in pilot/smart-factory data and common city-yearbook tables.
# Add aliases as needed. The script also leaves unknown names as cleaned pinyin-unmapped Chinese in diagnostics.
CITY_ZH_TO_EN = {
    "北京市": "Beijing", "北京": "Beijing",
    "上海市": "Shanghai", "上海": "Shanghai",
    "天津市": "Tianjin", "天津": "Tianjin",
    "重庆市": "Chongqing", "重庆": "Chongqing",
    "杭州市": "Hangzhou", "杭州": "Hangzhou",
    "合肥市": "Hefei", "合肥": "Hefei",
    "深圳市": "Shenzhen", "深圳": "Shenzhen",
    "德清县": "Deqing County", "德清": "Deqing County",
    "成都市": "Chengdu", "成都": "Chengdu",
    "济南市": "Jinan", "济南": "Jinan",
    "西安市": "Xi'an", "西安": "Xi'an",
    "广州市": "Guangzhou", "广州": "Guangzhou",
    "武汉市": "Wuhan", "武汉": "Wuhan",
    "苏州市": "Suzhou", "苏州": "Suzhou",
    "长沙市": "Changsha", "长沙": "Changsha",
    "郑州市": "Zhengzhou", "郑州": "Zhengzhou",
    "沈阳市": "Shenyang", "沈阳": "Shenyang",
    "青岛市": "Qingdao", "青岛": "Qingdao",
    "宁波市": "Ningbo", "宁波": "Ningbo",
    "无锡市": "Wuxi", "无锡": "Wuxi",
    "南京市": "Nanjing", "南京": "Nanjing",
    "常州市": "Changzhou", "常州": "Changzhou",
    "南通市": "Nantong", "南通": "Nantong",
    "盐城市": "Yancheng", "盐城": "Yancheng",
    "连云港市": "Lianyungang", "连云港": "Lianyungang",
    "镇江市": "Zhenjiang", "镇江": "Zhenjiang",
    "温州市": "Wenzhou", "温州": "Wenzhou",
    "金华市": "Jinhua", "金华": "Jinhua",
    "厦门市": "Xiamen", "厦门": "Xiamen",
    "潍坊市": "Weifang", "潍坊": "Weifang",
    "德州市": "Dezhou", "德州": "Dezhou",
    "烟台市": "Yantai", "烟台": "Yantai",
    "包头市": "Baotou", "包头": "Baotou",
    "西昌市": "Xichang", "西昌": "Xichang",
    "咸阳市": "Xianyang", "咸阳": "Xianyang",
    "秦皇岛市": "Qinhuangdao", "秦皇岛": "Qinhuangdao",
    "茂名市": "Maoming", "茂名": "Maoming",
    "洛阳市": "Luoyang", "洛阳": "Luoyang",
    "银川市": "Yinchuan", "银川": "Yinchuan",
    "乌鲁木齐市": "Urumqi", "乌鲁木齐": "Urumqi",
    "湛江市": "Zhanjiang", "湛江": "Zhanjiang",
    "绵阳市": "Mianyang", "绵阳": "Mianyang",
    "岳阳市": "Yueyang", "岳阳": "Yueyang",
    "临沂市": "Linyi", "临沂": "Linyi",
    "哈尔滨市": "Harbin", "哈尔滨": "Harbin",
    "唐山市": "Tangshan", "唐山": "Tangshan",
    "铜陵市": "Tongling", "铜陵": "Tongling",
    "芜湖市": "Wuhu", "芜湖": "Wuhu",
    "长春市": "Changchun", "长春": "Changchun",
    "太原市": "Taiyuan", "太原": "Taiyuan",
    "福州市": "Fuzhou", "福州": "Fuzhou",
    "南昌市": "Nanchang", "南昌": "Nanchang",
    "石家庄市": "Shijiazhuang", "石家庄": "Shijiazhuang",
    "大连市": "Dalian", "大连": "Dalian",
    "佛山市": "Foshan", "佛山": "Foshan",
    "东莞市": "Dongguan", "东莞": "Dongguan",
    "中山市": "Zhongshan", "中山": "Zhongshan",
    "珠海市": "Zhuhai", "珠海": "Zhuhai",
}

PROVINCE_ZH_TO_EN = {
    "北京": "Beijing", "北京市": "Beijing",
    "上海": "Shanghai", "上海市": "Shanghai",
    "天津": "Tianjin", "天津市": "Tianjin",
    "重庆": "Chongqing", "重庆市": "Chongqing",
    "浙江": "Zhejiang", "浙江省": "Zhejiang",
    "安徽": "Anhui", "安徽省": "Anhui",
    "广东": "Guangdong", "广东省": "Guangdong",
    "四川": "Sichuan", "四川省": "Sichuan",
    "山东": "Shandong", "山东省": "Shandong",
    "陕西": "Shaanxi", "陕西省": "Shaanxi",
    "湖北": "Hubei", "湖北省": "Hubei",
    "江苏": "Jiangsu", "江苏省": "Jiangsu",
    "湖南": "Hunan", "湖南省": "Hunan",
    "河南": "Henan", "河南省": "Henan",
    "辽宁": "Liaoning", "辽宁省": "Liaoning",
    "福建": "Fujian", "福建省": "Fujian",
    "吉林": "Jilin", "吉林省": "Jilin",
    "河北": "Hebei", "河北省": "Hebei",
    "内蒙古": "Inner Mongolia", "内蒙古自治区": "Inner Mongolia",
    "新疆": "Xinjiang", "新疆维吾尔自治区": "Xinjiang",
    "宁夏": "Ningxia", "宁夏回族自治区": "Ningxia",
    "黑龙江": "Heilongjiang", "黑龙江省": "Heilongjiang",
    "山西": "Shanxi", "山西省": "Shanxi",
    "江西": "Jiangxi", "江西省": "Jiangxi",
    "云南": "Yunnan", "云南省": "Yunnan",
    "贵州": "Guizhou", "贵州省": "Guizhou",
    "广西": "Guangxi", "广西壮族自治区": "Guangxi",
    "甘肃": "Gansu", "甘肃省": "Gansu",
    "青海": "Qinghai", "青海省": "Qinghai",
    "海南": "Hainan", "海南省": "Hainan",
}

# Provinces in yearbook order. Used to forward-fill province when tables have province header rows.
PROVINCE_NAMES = set(PROVINCE_ZH_TO_EN)

VAR_PATTERNS = {
    "population": ["人口数", "人口状况"],
    "gdp": ["地区生产总值"],
    "secondary_value_added": ["地区生产总值构成"],
    "employment": ["劳动力就业", "就业"],
    "average_wage": ["收入状况", "工资"],
    "industrial_output": ["规模以上工业", "工业"],
    "fixed_asset_investment": ["固定资产投资", "投资"],
    "fdi": ["外商", "实际使用外资", "外资"],
    "foreign_trade": ["对外经济贸易", "进出口", "外贸"],
    "education_proxy": ["教育", "学生"],
    "telecom_or_internet_proxy": ["邮电", "电信", "互联网", "宽带"],
}


def clean_cell(x: object) -> str:
    if pd.isna(x):
        return ""
    s = unicodedata.normalize("NFKC", str(x)).strip()
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def numeric(x: object) -> float:
    s = clean_cell(x)
    if not s or s in {"—", "-", "--", "…", "nan"}:
        return np.nan
    s = s.replace(",", "")
    # Keep negatives/decimals only.
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else np.nan


def infer_year(path: Path) -> int | None:
    m = re.search(r"(20\d{2})", str(path))
    return int(m.group(1)) if m else None


TABLE_CODE_VARS = {
    "2-12": "foreign_trade",
    "2-28": "telecom_or_internet_proxy",
    "2-13": "industrial_output",
    "2-14": "industrial_output",
}

# Full-archive tables with reliable city rows (skip 2-10..2-11 etc. that mis-match keywords).
ALLOWED_EXTRACTED_CODES = {
    "2-1", "2-6", "2-7", "2-8", "2-12", "2-13", "2-14", "2-18",
    "2-19", "2-20", "2-21", "2-28",
}


def infer_variable(path: Path) -> str | None:
    name = path.name
    code = re.search(r"(?:20[0-9]{2}-)?([23]-[0-9]{1,2})", name.replace("_", "-"))
    if code and code.group(1) in TABLE_CODE_VARS:
        return TABLE_CODE_VARS[code.group(1)]
    # GDP composition must be checked before GDP.
    if "地区生产总值构成" in name:
        return "secondary_value_added"
    for var, pats in VAR_PATTERNS.items():
        if any(p in name for p in pats):
            return var
    # ChinaUTC 2021–2023 filenames often use table codes only (e.g. 2021-2-7.xlsx).
    if re.search(r"2[-_]18", name):
        return "employment"
    if re.search(r"2[-_]8", name) or re.search(r"2[-_]08", name):
        return "secondary_value_added"
    if re.search(r"2[-_]7", name):
        return "gdp"
    if re.search(r"2[-_]1", name):
        return "population"
    return None


def log(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="backslashreplace").decode("ascii"))


def candidate_excel_files() -> list[Path]:
    if not DL.exists():
        raise FileNotFoundError(f"Missing {DL}. Run scripts/24_fetch_chinautc_city_yearbook.py first.")
    files = sorted(list(DL.rglob("*.xlsx")) + list(DL.rglob("*.xls")))
    # Prefer prefecture-level 2-* tables over municipal-district 3-* tables. Keep full-extract files if named by variable.
    out = []
    for p in files:
        name = p.name
        # County-level yearbook tables (3-*) only; do not match year prefixes like 2023_.
        if re.search(r"(?:^|_)3-\d", name):
            continue
        if "extracted_" in str(p):
            code = re.search(r"(?:20[0-9]{2}-)?([23]-[0-9]{1,2})", name.replace("_", "-"))
            if not code or code.group(1) not in ALLOWED_EXTRACTED_CODES:
                continue
        if infer_variable(p) is not None:
            out.append(p)
    return out


def read_table(path: Path) -> pd.DataFrame:
    # Read first sheet without trusting headers.
    try:
        raw = pd.read_excel(path, header=None, dtype=object)
    except Exception:
        raw = pd.read_excel(path, header=None, dtype=object, engine="openpyxl")
    # Drop empty rows/cols.
    raw = raw.dropna(how="all").dropna(axis=1, how="all")
    return raw


def row_contains_city(row: pd.Series) -> tuple[str, str] | None:
    texts = [clean_cell(v) for v in row.tolist()]
    joined = " ".join(texts)
    # Exact known city token anywhere in first three cells is safest.
    for cell in texts[:4]:
        if not cell:
            continue
        stripped = cell.replace(" ", "")
        if stripped in CITY_ZH_TO_EN:
            return stripped, CITY_ZH_TO_EN[stripped]
        # Some yearbook rows append administrative labels or numbering.
        for zh, en in CITY_ZH_TO_EN.items():
            if zh and zh in stripped and len(stripped) <= len(zh) + 4:
                return zh, en
    return None


def detect_province_row(row: pd.Series) -> str | None:
    texts = [clean_cell(v).replace(" ", "") for v in row.tolist()[:3]]
    for cell in texts:
        if cell in PROVINCE_NAMES:
            return PROVINCE_ZH_TO_EN[cell]
    return None


def pick_value_for_var(row: pd.Series, var: str) -> float:
    vals = [numeric(v) for v in row.tolist()]
    vals = [v for v in vals if not pd.isna(v)]
    if not vals:
        return np.nan
    # Heuristics by table type. Usually the first numeric after city is the relevant total.
    # GDP composition tables often contain primary/secondary/tertiary columns; secondary is often the 2nd or 3rd numeric.
    if var == "secondary_value_added" and len(vals) >= 3:
        # Prefer second industry value if columns are primary/secondary/tertiary; if table has GDP + shares, this is imperfect.
        return vals[1]
    if var == "average_wage" and len(vals) >= 2:
        # In labor/income tables first may be employment, later wage. Use largest plausible wage-like value.
        candidates = [v for v in vals if v > 1000]
        return candidates[-1] if candidates else vals[-1]
    if var == "telecom_or_internet_proxy" and len(vals) >= 3:
        # 2-28: postal revenue, telecom revenue, mobile subscribers (万户) — use subscribers.
        return vals[2]
    if var == "foreign_trade" and len(vals) >= 2:
        # 2-12: import + export (万元); store combined trade volume.
        return vals[0] + vals[1]
    return vals[0]


def parse_file(path: Path) -> pd.DataFrame:
    year = infer_year(path)
    var = infer_variable(path)
    if year is None or var is None:
        return pd.DataFrame()
    raw = read_table(path)
    rows = []
    current_province = ""
    for _, row in raw.iterrows():
        prov = detect_province_row(row)
        if prov:
            current_province = prov
            continue
        city_hit = row_contains_city(row)
        if not city_hit:
            continue
        city_zh, city_en = city_hit
        value = pick_value_for_var(row, var)
        if pd.isna(value):
            continue
        rows.append({
            "city": city_en,
            "city_zh": city_zh,
            "province": current_province,
            "year": year,
            "variable": var,
            "value": value,
            "source_file": path.name,
        })
    return pd.DataFrame(rows)


def build_controls() -> pd.DataFrame:
    files = candidate_excel_files()
    if not files:
        raise FileNotFoundError(f"No candidate XLSX/XLS files under {DL}")
    log(f"Parsing {len(files)} candidate Excel files")
    parsed = []
    for p in files:
        df = parse_file(p)
        log(f"{p.name}: {len(df)} parsed rows ({infer_variable(p)})")
        if not df.empty:
            parsed.append(df)
    if not parsed:
        raise RuntimeError("No data rows parsed. Inspect Excel file shapes and update parser heuristics.")
    long = pd.concat(parsed, ignore_index=True)
    # Combine duplicates by first non-null; there may be two GDP rows from multiple extracts.
    wide = (
        long.sort_values(["city", "year", "variable", "source_file"])
        .drop_duplicates(["city", "year", "variable"], keep="first")
        .pivot_table(index=["city", "year"], columns="variable", values="value", aggfunc="first")
        .reset_index()
    )
    wide.columns.name = None
    # Recover province by most common parsed province per city-year or city.
    prov = long.dropna(subset=["province"]).copy()
    prov = prov[prov["province"].astype(str).str.len() > 0]
    if not prov.empty:
        city_prov = prov.groupby("city")["province"].agg(lambda s: s.mode().iloc[0] if not s.mode().empty else s.iloc[0])
        wide["province"] = wide["city"].map(city_prov)
    else:
        wide["province"] = ""

    # Derive per-capita GDP when possible. Units will follow source table units and are not harmonized.
    if "gdp" in wide.columns and "population" in wide.columns:
        gdp = pd.to_numeric(wide["gdp"], errors="coerce")
        pop = pd.to_numeric(wide["population"], errors="coerce")
        wide["gdp_per_capita"] = np.where(pop > 0, gdp / pop, np.nan)
    else:
        wide["gdp_per_capita"] = np.nan

    # Ensure all contract columns exist.
    for col in REQUIRED:
        if col not in wide.columns:
            wide[col] = np.nan
    wide["source_name"] = "ChinaUTC_China_City_Statistical_Yearbook_public_fallback_units_as_reported"
    wide["source_file"] = "chinautc_downloads"
    out = wide[REQUIRED].copy()
    out = out.sort_values(["city", "year"])
    return out


def main() -> int:
    out = build_controls()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    miss = []
    for col in REQUIRED:
        if col in {"city", "province", "year", "source_name", "source_file"}:
            continue
        miss.append({
            "variable": col,
            "share_missing": float(out[col].isna().mean()),
            "n_missing": int(out[col].isna().sum()),
            "n_obs": int(len(out)),
            "nonmissing_years": sorted(out.loc[out[col].notna(), "year"].dropna().astype(int).unique().tolist()),
        })
    pd.DataFrame(miss).to_csv(MISS, index=False, encoding="utf-8-sig")
    log(f"Wrote {len(out)} city-year rows to {OUT}")
    log(f"Missingness report: {MISS}")
    log("Next commands:")
    log("  python scripts/06a_validate_city_controls_raw.py")
    log("  make city-controls")
    log("  make panel")
    log("  make analysis")
    log("  make production-check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
