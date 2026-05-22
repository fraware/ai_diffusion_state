"""Fetch public ChinaUTC China City Statistical Yearbook attachment files.

This script is a public-data fallback for Workstream A. It does not replace EPS if
EPS is available, but it makes the ChinaUTC route operational. It downloads the
public XLSX/RAR attachments exposed on ChinaUTC yearbook pages into:

    data/raw/city_controls/chinautc_downloads/

The script should be run on a local machine with internet access. The current
execution container cannot resolve chinautc.com, but ordinary browsers and local
PowerShell/curl generally can.

Sources verified by web inspection:
- 2024 index: https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6328
- 2023 index: https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6277
- 2022 index: https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6203
- 2021 index: https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6114
- 2019 index: https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=4849

2020 is sparse on ChinaUTC; if you need 2020 controls, use EPS/CNKI or the full
paid/mirrored yearbook source.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urljoin, unquote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "city_controls" / "chinautc_downloads"
BASE = "https://www.chinautc.com"

INDEX_PAGES = {
    2024: "https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6328",
    2023: "https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6277",
    2022: "https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6203",
    2021: "https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=6114",
    2019: "https://www.chinautc.com/templates/H_nianjian/index.aspx?nodeid=4849",
}

# Tables most relevant to the repo contract. The full RAR is best when available.
KEY_TERMS = [
    "人口",
    "地区生产总值",
    "地区生产总值构成",
    "劳动力就业",
    "收入状况",
    "对外经济贸易",
    "规模以上工业",
    "固定资产投资",
    "学生数",
    "邮政",
    "电信",
    "互联网",
    "中国城市统计年鉴",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Referer": "https://www.chinautc.com/",
}


@dataclass
class Attachment:
    year: int
    page_url: str
    url: str
    name: str


def get_html(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def discover_content_pages(year: int, index_url: str) -> list[str]:
    html = get_html(index_url)
    soup = BeautifulSoup(html, "html.parser")
    pages: list[str] = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)
        href = a["href"]
        if "ContentPage" not in href and "contentid=" not in href:
            continue
        if any(term in text for term in KEY_TERMS):
            pages.append(urljoin(index_url, href))
    return sorted(set(pages))


def discover_attachments(year: int, content_url: str) -> list[Attachment]:
    html = get_html(content_url)
    soup = BeautifulSoup(html, "html.parser")
    out: list[Attachment] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)
        if not any(href.lower().endswith(ext) for ext in [".xlsx", ".xls", ".rar", ".zip"]):
            continue
        abs_url = urljoin(content_url, href)
        name = unquote(abs_url.rsplit("/", 1)[-1]) or text
        out.append(Attachment(year=year, page_url=content_url, url=abs_url, name=name))
    return out


def safe_filename(year: int, name: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", "_", name).strip()
    return f"{year}_{cleaned}"


def download(att: Attachment) -> Path:
    year_dir = OUT_DIR / str(att.year)
    year_dir.mkdir(parents=True, exist_ok=True)
    path = year_dir / safe_filename(att.year, att.name)
    if path.exists() and path.stat().st_size > 0:
        print(f"SKIP exists: {path}")
        return path
    print(f"Downloading {att.url}")
    with requests.get(att.url, headers={**HEADERS, "Referer": att.page_url}, stream=True, timeout=120) as r:
        r.raise_for_status()
        with path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
    print(f"Wrote {path} ({path.stat().st_size} bytes)")
    return path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_atts: list[Attachment] = []
    for year, index_url in INDEX_PAGES.items():
        print(f"\n=== {year}: {index_url} ===")
        try:
            pages = discover_content_pages(year, index_url)
        except Exception as exc:
            print(f"FAILED index {year}: {exc}")
            continue
        print(f"Found {len(pages)} content pages")
        for p in pages:
            try:
                all_atts.extend(discover_attachments(year, p))
            except Exception as exc:
                print(f"FAILED content page {p}: {exc}")
    # Deduplicate by URL.
    uniq: dict[str, Attachment] = {a.url: a for a in all_atts}
    print(f"\nDiscovered {len(uniq)} attachment URLs")
    manifest_rows = []
    for att in uniq.values():
        try:
            path = download(att)
            status = "downloaded"
        except Exception as exc:
            path = Path("")
            status = f"failed: {exc}"
            print(f"FAILED download {att.url}: {exc}")
        manifest_rows.append({
            "year": att.year,
            "page_url": att.page_url,
            "attachment_url": att.url,
            "name": att.name,
            "local_path": str(path),
            "status": status,
        })
    import csv
    manifest = OUT_DIR / "chinautc_manifest.csv"
    with manifest.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()) if manifest_rows else ["year","page_url","attachment_url","name","local_path","status"])
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"\nManifest: {manifest}")
    print("Next: inspect downloaded files, extract RAR/ZIP if needed, and build a normalized city-controls CSV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
