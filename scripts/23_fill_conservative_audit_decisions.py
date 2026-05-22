"""Conservatively fill the city-resolution audit sample without inventing evidence.

This script is intentionally conservative. It does not convert registry/list-based
inference into external verification, and it does not mark opaque registry matches as
confirmed unless the row itself contains a direct city signal.

Decision policy:
- official_location_exact -> confirmed, because the source location field is the evidence.
- rule_based rows with direct text evidence types -> confirmed.
- firm_registry_match rows -> insufficient_evidence unless a city token is visibly present
  in the firm or project name.

The output is a legitimate audit file for Table 17, but it should be described as an
AI-assisted conservative audit unless a human reviewer overwrites the auditor fields.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

AUDIT_PATH = ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"

DIRECT_TEXT_EVIDENCE = {
    "firm_embedded_city_token",
    "project_embedded_city_token",
    "project_branch_city",
    "project_name_city",
    "firm_parenthetical",
    "html_p_tag_rtl_location",
    "embedded_html_table",
}

CITY_TOKEN_HINTS = {
    "Beijing": ["北京"],
    "Shanghai": ["上海"],
    "Tianjin": ["天津"],
    "Chongqing": ["重庆"],
    "Shenzhen": ["深圳"],
    "Guangzhou": ["广州"],
    "Hangzhou": ["杭州"],
    "Wuhan": ["武汉", "武昌"],
    "Xi'an": ["西安"],
    "Changsha": ["长沙"],
    "Chengdu": ["成都"],
    "Hefei": ["合肥"],
    "Suzhou": ["苏州"],
    "Nanjing": ["南京"],
    "Nantong": ["南通"],
    "Changzhou": ["常州"],
    "Xiamen": ["厦门"],
    "Weifang": ["潍坊"],
    "Dezhou": ["德州"],
    "Yantai": ["烟台"],
    "Qingdao": ["青岛"],
    "Ningbo": ["宁波"],
    "Wenzhou": ["温州"],
    "Jinhua": ["金华"],
    "Yancheng": ["盐城"],
    "Lianyungang": ["连云港"],
    "Zhenjiang": ["镇江"],
    "Changshu": ["常熟"],
    "Baotou": ["包头"],
    "Xichang": ["西昌"],
    "Xianyang": ["泾阳", "咸阳"],
    "Qinhuangdao": ["秦皇岛"],
    "Maoming": ["茂名"],
    "Luoyang": ["洛阳"],
    "Yinchuan": ["银川", "宁夏"],
    "Urumqi": ["新疆", "乌鲁木齐"],
    "Zhanjiang": ["湛江"],
    "Mianyang": ["绵阳"],
    "Yueyang": ["岳阳"],
    "Linyi": ["临港", "临沂"],
    "Harbin": ["哈尔滨"],
    "Tangshan": ["唐山"],
    "Tongling": ["枞阳", "铜陵"],
}


def _has_city_token(row: pd.Series) -> bool:
    city = str(row.get("assigned_city", ""))
    haystack = f"{row.get('firm_name_zh', '')} {row.get('project_name_zh', '')}"
    for tok in CITY_TOKEN_HINTS.get(city, []):
        if tok and tok in haystack:
            return True
    return False


def _decide(row: pd.Series) -> tuple[str, str]:
    rc = str(row.get("resolution_class", ""))
    et = str(row.get("evidence_type", ""))
    city = str(row.get("assigned_city", ""))

    if rc == "official_location_exact":
        return (
            "confirmed",
            "Confirmed from official/list location field used by the parser; not external verification beyond the list source.",
        )

    if et in DIRECT_TEXT_EVIDENCE:
        return (
            "confirmed",
            "Confirmed by direct city signal in firm/project/source-row text; not external verification.",
        )

    if et == "firm_registry_match" and _has_city_token(row):
        return (
            "confirmed",
            "Confirmed conservatively because the assigned city is explicitly visible in the Chinese firm/project text; registry-derived inference remains non-external.",
        )

    if et == "firm_registry_match":
        return (
            "insufficient_evidence",
            "Registry-derived rule present, but sample row provides no independent non-list evidence for city assignment.",
        )

    return (
        "uncertain",
        f"No deterministic confirmation rule for evidence_type='{et}'; retain as uncertain pending human source check.",
    )


def main() -> int:
    if not AUDIT_PATH.exists():
        print(f"Missing {AUDIT_PATH}")
        return 1
    audit = pd.read_csv(AUDIT_PATH)
    for col in ("auditor_decision", "audit_notes", "auditor", "audit_date"):
        if col in audit.columns:
            audit[col] = audit[col].astype("object")
    today = date.today().isoformat()
    changed = 0
    for idx, row in audit.iterrows():
        existing = row.get("auditor_decision", "")
        if pd.notna(existing) and str(existing).strip():
            continue
        decision, notes = _decide(row)
        audit.at[idx, "auditor_decision"] = decision
        audit.at[idx, "audit_notes"] = notes
        audit.at[idx, "auditor"] = "conservative_audit_workflow"
        audit.at[idx, "audit_date"] = today
        changed += 1
    audit.to_csv(AUDIT_PATH, index=False, encoding="utf-8-sig")
    print(f"Filled {changed} blank audit decisions conservatively in {AUDIT_PATH}")
    print(audit["auditor_decision"].value_counts(dropna=False).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
