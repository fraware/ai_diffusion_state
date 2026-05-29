# scripts/79_lens_geography_export.py
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

LENS_URL = "https://api.lens.org/patent/search"

CONTRACT_COLUMNS = [
    "patent_id",
    "applicant_city",
    "applicant_province",
    "applicant_address",
    "geo_source",
    "geo_match_confidence",
    "geo_notes",
]

PROVINCES_EN = [
    "Anhui", "Fujian", "Gansu", "Guangdong", "Guizhou", "Hainan", "Hebei",
    "Heilongjiang", "Henan", "Hubei", "Hunan", "Jiangsu", "Jiangxi", "Jilin",
    "Liaoning", "Qinghai", "Shaanxi", "Shandong", "Shanxi", "Sichuan",
    "Yunnan", "Zhejiang", "Taiwan",
    "Inner Mongolia", "Guangxi", "Ningxia", "Xinjiang", "Tibet",
    "Beijing", "Shanghai", "Tianjin", "Chongqing",
    "Hong Kong", "Macau",
]

PROVINCES_ZH = {
    "安徽": "Anhui",
    "福建": "Fujian",
    "甘肃": "Gansu",
    "广东": "Guangdong",
    "贵州": "Guizhou",
    "海南": "Hainan",
    "河北": "Hebei",
    "黑龙江": "Heilongjiang",
    "河南": "Henan",
    "湖北": "Hubei",
    "湖南": "Hunan",
    "江苏": "Jiangsu",
    "江西": "Jiangxi",
    "吉林": "Jilin",
    "辽宁": "Liaoning",
    "青海": "Qinghai",
    "陕西": "Shaanxi",
    "山东": "Shandong",
    "山西": "Shanxi",
    "四川": "Sichuan",
    "云南": "Yunnan",
    "浙江": "Zhejiang",
    "内蒙古": "Inner Mongolia",
    "广西": "Guangxi",
    "宁夏": "Ningxia",
    "新疆": "Xinjiang",
    "西藏": "Tibet",
    "北京": "Beijing",
    "上海": "Shanghai",
    "天津": "Tianjin",
    "重庆": "Chongqing",
    "香港": "Hong Kong",
    "澳门": "Macau",
}

MUNICIPALITIES = {"Beijing", "Shanghai", "Tianjin", "Chongqing"}

CITY_SUFFIX_RE = re.compile(r"([\u4e00-\u9fff]{2,12})市")


def norm_id(x: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(x or "").upper())


def read_ids(path: Path, limit: int | None = None) -> list[str]:
    ids: list[str] = []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = (row.get("publication_number") or row.get("patent_id") or "").strip()
            if pid:
                ids.append(pid)
            if limit and len(ids) >= limit:
                break
    return ids


def chunks(xs: list[str], n: int):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def _ssl_verify(insecure: bool) -> bool:
    if insecure:
        return False
    flag = os.environ.get("LENS_INSECURE_SSL", "").strip().lower()
    return flag not in {"1", "true", "yes"}


def lens_request(
    token: str,
    ids: list[str],
    include: list[str] | None,
    timeout: int,
    sleep: float,
    *,
    verify_ssl: bool = True,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "query": {
            "terms": {
                "ids": ids
            }
        },
        "size": len(ids),
        "stemming": False,
    }
    if include is not None:
        body["include"] = include

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    for attempt in range(8):
        r = requests.post(
            LENS_URL,
            headers=headers,
            data=json.dumps(body),
            timeout=timeout,
            verify=verify_ssl,
        )
        if r.status_code == 429:
            wait = max(sleep, 8.0) * (attempt + 1)
            print(
                f"429 rate limited; sleeping {wait:.1f}s",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(wait)
            continue
        if r.status_code >= 500:
            wait = max(sleep, 5.0) * (attempt + 1)
            print(
                f"{r.status_code} server error; sleeping {wait:.1f}s",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(wait)
            continue
        if r.status_code != 200:
            print("Lens error status:", r.status_code, file=sys.stderr)
            print(r.text[:2000], file=sys.stderr)
            r.raise_for_status()
        return r.json()

    raise RuntimeError("Lens API failed after retries")


def get_path(d: dict[str, Any], path: list[str], default=None):
    cur: Any = d
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
    return cur if cur is not None else default


def candidate_ids(record: dict[str, Any]) -> set[str]:
    cands: set[str] = set()

    for key in ("doc_key", "lens_id"):
        val = record.get(key)
        if val:
            cands.add(norm_id(str(val)))

    jurisdiction = str(record.get("jurisdiction") or "").strip()
    doc_number = str(record.get("doc_number") or "").strip()
    kind = str(record.get("kind") or "").strip()
    if jurisdiction and doc_number:
        cands.add(norm_id(jurisdiction + doc_number))
        if kind:
            cands.add(norm_id(jurisdiction + doc_number + kind))

    pub_ref = get_path(record, ["biblio", "publication_reference"], {})
    if isinstance(pub_ref, dict):
        j = str(pub_ref.get("jurisdiction") or "").strip()
        dn = str(pub_ref.get("doc_number") or "").strip()
        k = str(pub_ref.get("kind") or "").strip()
        if j and dn:
            cands.add(norm_id(j + dn))
            if k:
                cands.add(norm_id(j + dn + k))

    return {c for c in cands if c}


def _party_name(party: dict[str, Any]) -> str:
    name_obj = party.get("extracted_name")
    if isinstance(name_obj, dict):
        return str(name_obj.get("value") or "").strip()
    return str(name_obj or "").strip()


def _party_address(party: dict[str, Any]) -> str:
    for key in ("extracted_address", "address"):
        val = party.get(key)
        if isinstance(val, dict):
            val = val.get("value")
        text = str(val or "").strip()
        if text:
            return text
    return ""


def extract_first_applicant(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return (name, address, confidence_suffix). suffix is '' for applicant address."""
    applicants = get_path(record, ["biblio", "parties", "applicants"], [])
    if isinstance(applicants, list):
        for app in applicants:
            if not isinstance(app, dict):
                continue
            address = _party_address(app)
            if address:
                return _party_name(app), address, ""

    inventors = get_path(record, ["biblio", "parties", "inventors"], [])
    if isinstance(inventors, list):
        for inv in inventors:
            if not isinstance(inv, dict):
                continue
            address = _party_address(inv)
            if address:
                return _party_name(inv), address, "_inventor_fallback"

    if isinstance(applicants, list) and applicants and isinstance(applicants[0], dict):
        return _party_name(applicants[0]), "", ""

    return "", "", ""


def parse_china_geo(address: str) -> tuple[str, str]:
    if not address:
        return "", ""

    text = str(address).strip()

    province = ""
    city = ""

    for zh, en in PROVINCES_ZH.items():
        if zh in text:
            province = en
            if en in MUNICIPALITIES:
                city = en
            break

    m = CITY_SUFFIX_RE.search(text)
    if m:
        city = m.group(1)
        if city.endswith("市"):
            city = city[:-1]

    upper_clean = re.sub(r"\s+", " ", text.replace(",", " ")).strip().lower()
    for p in sorted(PROVINCES_EN, key=len, reverse=True):
        if p.lower() in upper_clean:
            province = province or p
            if p in MUNICIPALITIES:
                city = city or p
            break

    if province and not city:
        parts = [x.strip() for x in re.split(r"[,;，；]", text) if x.strip()]
        for idx, part in enumerate(parts):
            if province.lower() in part.lower() and idx > 0:
                prev = parts[idx - 1]
                if 2 <= len(prev) <= 40:
                    city = prev
                    break

    return city, province


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--chunk-size", type=int, default=100)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--token-env", default="LENS_API_TOKEN")
    ap.add_argument(
        "--insecure-ssl",
        action="store_true",
        help="Disable TLS cert verification (or set LENS_INSECURE_SSL=1)",
    )
    args = ap.parse_args()
    verify_ssl = _ssl_verify(args.insecure_ssl)

    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit(f"Missing ${args.token_env}")

    ids = read_ids(args.input, limit=args.limit or None)
    if not ids:
        raise SystemExit(f"No IDs found in {args.input}")

    include = [
        "lens_id",
        "jurisdiction",
        "doc_number",
        "kind",
        "doc_key",
        "date_published",
        "biblio",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    matched_records = 0
    address_rows = 0
    city_rows = 0
    province_rows = 0

    with args.output.open("w", encoding="utf-8-sig", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=CONTRACT_COLUMNS)
        writer.writeheader()

        for batch_no, id_chunk in enumerate(chunks(ids, args.chunk_size), start=1):
            input_by_norm = {norm_id(x): x for x in id_chunk}
            data = lens_request(
                token,
                id_chunk,
                include,
                args.timeout,
                args.sleep,
                verify_ssl=verify_ssl,
            )
            records = data.get("data") or []

            found_norms: set[str] = set()

            for rec in records:
                cands = candidate_ids(rec)
                matched_input = ""
                for c in cands:
                    if c in input_by_norm:
                        matched_input = input_by_norm[c]
                        found_norms.add(c)
                        break

                if not matched_input:
                    joined = " ".join(cands)
                    for k, original in input_by_norm.items():
                        if k and k in joined:
                            matched_input = original
                            found_norms.add(k)
                            break

                if not matched_input:
                    continue

                _name, address, conf_suffix = extract_first_applicant(rec)
                city, province = parse_china_geo(address)
                confidence = (
                    "exact_publication_number_address_parsed"
                    if address
                    else "exact_publication_number_no_address_in_lens"
                )
                if conf_suffix and address:
                    confidence = f"exact_publication_number{conf_suffix}"

                notes = (
                    "Lens applicant extracted_address; city/province parsed locally"
                    if not conf_suffix
                    else "Lens inventor address fallback; city/province parsed locally"
                )
                if not address:
                    notes = "Lens record matched by publication id but no applicant address field"

                writer.writerow({
                    "patent_id": matched_input,
                    "applicant_city": city,
                    "applicant_province": province,
                    "applicant_address": address,
                    "geo_source": "Lens Patent API",
                    "geo_match_confidence": confidence,
                    "geo_notes": notes,
                })

                written += 1
                matched_records += 1
                if address:
                    address_rows += 1
                if city:
                    city_rows += 1
                if province:
                    province_rows += 1

            for k, original in input_by_norm.items():
                if k not in found_norms:
                    writer.writerow({
                        "patent_id": original,
                        "applicant_city": "",
                        "applicant_province": "",
                        "applicant_address": "",
                        "geo_source": "Lens Patent API",
                        "geo_match_confidence": "not_found",
                        "geo_notes": (
                            "No Lens record returned for publication-number query"
                        ),
                    })
                    written += 1

            if batch_no % 10 == 0 or batch_no == 1:
                print({
                    "batch_no": batch_no,
                    "input_processed": min(batch_no * args.chunk_size, len(ids)),
                    "written": written,
                    "matched_records": matched_records,
                    "address_fill": round(address_rows / max(written, 1), 4),
                    "city_fill": round(city_rows / max(written, 1), 4),
                    "province_fill": round(province_rows / max(written, 1), 4),
                }, flush=True)

            time.sleep(args.sleep)

    print({
        "input_ids": len(ids),
        "written_rows": written,
        "matched_records": matched_records,
        "address_rows": address_rows,
        "city_rows": city_rows,
        "province_rows": province_rows,
        "address_fill": round(address_rows / max(written, 1), 4),
        "city_fill": round(city_rows / max(written, 1), 4),
        "province_fill": round(province_rows / max(written, 1), 4),
        "output": str(args.output),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
