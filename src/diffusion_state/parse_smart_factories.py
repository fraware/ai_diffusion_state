from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from diffusion_state.utils import PROJECT_ROOT, read_yaml, write_csv

SOURCE_2024 = "https://cn.solarbe.com/news/20250103/92225.html"
SOURCE_2025 = "https://jlts.com.cn/i/news/detail/2571072131159669662.html"
EXPECTED_2024 = 235
EXPECTED_2025 = 274

RANK_LINE_RE = re.compile(r"^(\d{1,3})\s+(.+)$")
LOCATION_SUFFIX_RE = re.compile(
    r"([\u4e00-\u9fff]{2,}(?:省|市|自治区|特别行政区))\s*$"
)
FIRM_SUFFIX_RE = re.compile(
    r"^(.+?(?:股份有限公司|集团有限公司|有限公司|集团公司|公司|研究院|研究所|"
    r"石化分公司|卷烟厂|装置部|工厂|矿务局|电厂|矿场))"
)


def _location_suffix_tokens() -> list[str]:
    cfg = read_yaml(PROJECT_ROOT / "configs" / "province_normalization.yml")
    tokens = list(cfg.get("municipalities", {}).keys()) + list(cfg.get("provinces", {}).keys())
    return sorted(set(tokens), key=len, reverse=True)


def parse_2024_list_line(text: str) -> dict | None:
    """Parse one Solarbe <p> row: rank, firm, project, location.

    Location is the trailing administrative unit. Firm is the prefix ending in 公司/集团/etc.
    This avoids splitting project names that contain spaces (e.g. 'AI 大模型...').
    """
    text = text.strip().replace("\xa0", "")
    m = RANK_LINE_RE.match(text)
    if not m:
        return None
    rank = int(m.group(1))
    rest = m.group(2).strip()

    location = None
    for token in _location_suffix_tokens():
        if rest.endswith(token):
            location = token
            body = rest[: -len(token)].strip()
            break
    if location is None:
        loc_m = LOCATION_SUFFIX_RE.search(rest)
        if not loc_m:
            return None
        location = loc_m.group(1).strip()
        body = rest[: loc_m.start()].strip()

    firm_m = FIRM_SUFFIX_RE.match(body)
    if firm_m:
        firm = firm_m.group(1).strip()
        project = body[firm_m.end() :].strip()
    else:
        parts = body.split(maxsplit=1)
        if len(parts) < 2:
            return None
        firm, project = parts[0].strip(), parts[1].strip()

    if not firm or not project or not location:
        return None
    return {
        "rank": rank,
        "firm_name_zh": firm,
        "project_name_zh": project,
        "location_raw": location,
    }


def parse_2024_mirror_html(path: Path) -> pd.DataFrame:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    rows: list[dict] = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        parsed = parse_2024_list_line(text)
        if parsed:
            rows.append(parsed)
    if len(rows) != EXPECTED_2024:
        raise ValueError(
            f"2024 parser expected {EXPECTED_2024} rows from {path.name}, got {len(rows)}"
        )
    df = pd.DataFrame(rows)
    df["list_year"] = 2024
    df["batch"] = "2024_first_batch"
    df["source_url"] = SOURCE_2024
    df["source_file"] = path.name
    df["parse_method"] = "html_p_tag_rtl_location"
    return df.sort_values("rank").reset_index(drop=True)


def parse_2025_jlts_html(path: Path) -> pd.DataFrame:
    html = path.read_text(encoding="utf-8", errors="ignore")
    header_idx = html.find(">序号</td>")
    if header_idx < 0:
        raise ValueError(f"No table header found in {path.name}")
    table_start = html.rfind("<table", 0, header_idx)
    table_end = html.find("</table>", table_start) + len("</table>")
    frag = html[table_start:table_end]
    soup = BeautifulSoup(frag, "lxml")
    rows: list[dict] = []
    for tr in soup.find_all("tr"):
        tds = [td.get_text(strip=True).replace("\xa0", "") for td in tr.find_all("td")]
        if len(tds) < 4:
            continue
        if not re.fullmatch(r"\d{1,3}", tds[0]):
            continue
        rows.append(
            {
                "rank": int(tds[0]),
                "firm_name_zh": tds[1],
                "project_name_zh": tds[2],
                "location_raw": tds[3],
            }
        )
    if len(rows) != EXPECTED_2025:
        raise ValueError(
            f"2025 parser expected {EXPECTED_2025} rows from {path.name}, got {len(rows)}"
        )
    df = pd.DataFrame(rows)
    df["list_year"] = 2025
    df["batch"] = "2025_excellence_batch"
    df["source_url"] = SOURCE_2025
    df["source_file"] = path.name
    df["parse_method"] = "embedded_html_table"
    return df.sort_values("rank").reset_index(drop=True)


def parse_smart_factory_lists(
    raw_dir: Path | None = None,
    interim_dir: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_dir = raw_dir or PROJECT_ROOT / "data" / "raw" / "smart_factories"
    interim_dir = interim_dir or PROJECT_ROOT / "data" / "interim"
    interim_dir.mkdir(parents=True, exist_ok=True)

    path_2024 = raw_dir / "2024_mirror.html"
    path_2025 = raw_dir / "2025_jlts.html"
    if not path_2024.exists():
        raise FileNotFoundError(
            f"Missing {path_2024}. Run: python scripts/01_fetch_source_pages.py"
        )
    if not path_2025.exists():
        raise FileNotFoundError(
            f"Missing {path_2025}. Run: python scripts/01_fetch_source_pages.py"
        )

    df_2024 = parse_2024_mirror_html(path_2024)
    df_2025 = parse_2025_jlts_html(path_2025)
    write_csv(df_2024, interim_dir / "smart_factories_2024_raw.csv")
    write_csv(df_2025, interim_dir / "smart_factories_2025_raw.csv")
    return df_2024, df_2025


if __name__ == "__main__":
    y2024, y2025 = parse_smart_factory_lists()
    print(f"2024: {len(y2024)} rows; 2025: {len(y2025)} rows")
