from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from diffusion_state.utils import PROJECT_ROOT, normalize_cn_text, read_yaml, write_csv

PROVINCE_PATTERN = re.compile(
    r"(北京市|天津市|上海市|重庆市|河北省|山西省|辽宁省|吉林省|黑龙江省|江苏省|浙江省|安徽省|福建省|江西省|山东省|河南省|湖北省|湖南省|广东省|海南省|四川省|贵州省|云南省|陕西省|甘肃省|青海省|台湾省|内蒙古自治区|广西壮族自治区|西藏自治区|宁夏回族自治区|新疆维吾尔自治区|香港特别行政区|澳门特别行政区)"
)


def extract_tables_from_html(path: Path) -> list[pd.DataFrame]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    tables = []
    for table in soup.find_all("table"):
        try:
            dfs = pd.read_html(str(table))
            tables.extend(dfs)
        except ValueError:
            pass
    return tables


def parse_line_based_smart_factory_rows(text: str) -> pd.DataFrame:
    """Fallback parser for pages where the list appears as plain text rather than an HTML table.

    Expected row format is usually: serial number, firm name, project name, province/location.
    This parser deliberately errs on the side of collecting candidate rows for manual review.
    """
    rows = []
    for raw in text.splitlines():
        line = normalize_cn_text(raw)
        if not line:
            continue
        if not any(x in line for x in ["智能工厂", "人工智能", "数字孪生", "5G", "智能制造"]):
            continue
        province_match = PROVINCE_PATTERN.search(line)
        rows.append({
            "raw_line": line,
            "province_or_city_detected": province_match.group(1) if province_match else None,
        })
    return pd.DataFrame(rows)


def classify_smart_factory(df: pd.DataFrame) -> pd.DataFrame:
    keyword_cfg = read_yaml(PROJECT_ROOT / "configs" / "keywords_zh.yml")
    all_industrial = []
    for group in keyword_cfg["industrial_ai_keywords"].values():
        all_industrial.extend(group)

    text_cols = [c for c in df.columns if df[c].dtype == "object"]
    joined = df[text_cols].fillna("").agg(" ".join, axis=1)
    df = df.copy()
    df["industrial_ai_keyword_hit"] = joined.apply(lambda x: ";".join([k for k in all_industrial if k in str(x)]))
    df["has_industrial_ai_keyword"] = df["industrial_ai_keyword_hit"].str.len() > 0
    return df


def parse_smart_factories(raw_dir: Path | None = None, out_path: Path | None = None) -> pd.DataFrame:
    raw_dir = raw_dir or PROJECT_ROOT / "data" / "raw" / "source_pages"
    out_path = out_path or PROJECT_ROOT / "data" / "interim" / "smart_factories_candidates.csv"

    candidate_frames: list[pd.DataFrame] = []
    for path in raw_dir.glob("*smart_factory*.html"):
        tables = extract_tables_from_html(path)
        for i, table in enumerate(tables):
            table = table.copy()
            table["source_file"] = path.name
            table["source_table_index"] = i
            candidate_frames.append(table)
        if not tables:
            text = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml").get_text("\n")
            cand = parse_line_based_smart_factory_rows(text)
            if not cand.empty:
                cand["source_file"] = path.name
                candidate_frames.append(cand)

    if not candidate_frames:
        raise RuntimeError("No smart-factory candidate rows found. Check raw HTML or attachment parsing.")

    df = pd.concat(candidate_frames, ignore_index=True, sort=False)
    df = classify_smart_factory(df)
    write_csv(df, out_path)
    return df


if __name__ == "__main__":
    out = parse_smart_factories()
    print(out.shape)
