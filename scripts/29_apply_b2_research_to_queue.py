"""Apply documented B2 research URLs to external_verification_queue.csv.

Reads project_id / URL / evidence_type / notes from:
  docs/DEEP_RESEARCH_A_B2_FINDINGS.md
  docs/DEEP_RESEARCH_A_B2_ROUND2.md
  docs/DEEP_RESEARCH_A_B2_ROUND3.md

Does not invent URLs. Skips TBD and rows without https://.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

DOCS = [
    ROOT / "docs" / "DEEP_RESEARCH_A_B2_FINDINGS.md",
    ROOT / "docs" / "DEEP_RESEARCH_A_B2_ROUND2.md",
    ROOT / "docs" / "DEEP_RESEARCH_A_B2_ROUND3.md",
]
QUEUE = ROOT / "data" / "interim" / "external_verification_queue.csv"
PID_RE = re.compile(r"(20\d{2}_(?:20\d{2})_(?:first_batch|excellence_batch)_\d{4})")
URL_RE = re.compile(r"https?://[^\s|]+")
VALID_TYPES = {
    "company_annual_report",
    "company_site_registry",
    "industrial_park_page",
    "project_registry",
}

# Rows not yet in DEEP_RESEARCH memos; URLs verified in supplemental pass (2026-05-22).
B2_SUPPLEMENT: dict[str, dict[str, str]] = {
    "2024_2024_first_batch_0209": {
        "external_evidence_url": "https://job.tyust.edu.cn/detail/online?id=3347959&menu_id=",
        "external_evidence_type": "project_registry",
        "audit_notes": "University recruitment page lists庆安集团西安地址大庆路628号; third-party but non-list.",
    },
    "2025_2025_excellence_batch_0210": {
        "external_evidence_url": "https://www.hnlens.com/category/contact.html",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Official Lens Technology contact page; Changsha-area corporate location evidence.",
    },
    "2025_2025_excellence_batch_0248": {
        "external_evidence_url": "https://www.kelun.com/intro/6.html",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Official Kelun Pharma contact page; Chengdu headquarters address.",
    },
    "2025_2025_excellence_batch_0262": {
        "external_evidence_url": "https://www.sxqc.com/about/contact_us.htm",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Official Shaanxi Auto (陕汽) contact page; Xi'an address at泾渭工业园.",
    },
    "2025_2025_excellence_batch_0264": {
        "external_evidence_url": "https://m.sn.huatu.com/2020/0416/1031680.html",
        "external_evidence_type": "project_registry",
        "audit_notes": "Public recruitment notice lists西安航空计算技术研究所通信地址锦业二路15号; third-party but non-list.",
    },
    "2025_2025_excellence_batch_0088": {
        "external_evidence_url": "https://www.baosteel.com/meishan/",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Baosteel Meishan Steel subsidiary page; Shanghai-area corporate location evidence.",
    },
    "2025_2025_excellence_batch_0062": {
        "external_evidence_url": "https://www.lixiang.com/",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Li Auto corporate site; assigned city Beijing reflects HQ—Changzhou plant not separately verified here.",
    },
    "2024_2024_first_batch_0083": {
        "external_evidence_url": "https://www.zjtobacco.com.cn/",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Zhejiang Tobacco official site; Hangzhou corporate-location evidence.",
    },
    "2025_2025_excellence_batch_0111": {
        "external_evidence_url": "https://www.holley.cn/contact.html",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Official Holley contact page; Hangzhou address五常大道181号.",
    },
    "2025_2025_excellence_batch_0201": {
        "external_evidence_url": "https://www.midea.com/cn/",
        "external_evidence_type": "company_site_registry",
        "audit_notes": "Midea Group corporate site; Wuhan laundry subsidiary plant location not separately verified on this page.",
    },
    "2025_2025_excellence_batch_0252": {
        "external_evidence_url": "http://www.scspc.gov.cn/html/zd/dt/2009/0821/60438.html",
        "external_evidence_type": "project_registry",
        "audit_notes": "Sichuan provincial legislature profile of核动力院; local-government document supporting Chengdu-area assignment.",
    },
}


def parse_research_rows(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if "project_id" in line.lower() or "---" in line:
            continue
        m = PID_RE.search(line)
        if not m:
            continue
        pid = m.group(1)
        url_m = URL_RE.search(line)
        if not url_m:
            continue
        url = url_m.group(0).rstrip(").,;")
        if url.upper() == "TBD" or "TBD" in line.split(url, 1)[-1][:5]:
            continue
        parts = [p.strip() for p in line.split("|")]
        # | rank | pid | firm | city | url | type | notes |
        et = ""
        notes = ""
        for p in parts:
            if p in VALID_TYPES:
                et = p
        if not et:
            for p in parts:
                if p in VALID_TYPES:
                    et = p
                    break
        # fallback: token after URL in split
        if not et:
            idx = line.find(url)
            tail = line[idx + len(url) :]
            for t in VALID_TYPES:
                if t in tail:
                    et = t
                    break
        if not et:
            et = "company_site_registry"
        notes_parts = []
        if idx := line.find("|", line.find(url)):
            tail = line.split(url, 1)[-1]
            note_text = tail.split("|", 2)[-1].strip().rstrip("|").strip()
            if note_text and note_text not in VALID_TYPES:
                notes = note_text
        if "Corporate-location" not in notes and et == "company_site_registry":
            notes = (
                "Corporate-location evidence from documented B2 research; "
                "not necessarily project-specific plant-location evidence. "
                + notes
            ).strip()
        elif et == "project_registry" and "Third-party" not in notes:
            notes = (
                "Third-party or government registry evidence from documented B2 research. "
                + notes
            ).strip()
        elif et in {"company_annual_report", "industrial_park_page"} and not notes:
            notes = "External evidence from documented B2 research memo."
        out[pid] = {
            "external_evidence_url": url,
            "external_evidence_type": et,
            "audit_notes": notes[:500],
        }
    return out


def sync_queue_from_verified_seed() -> int:
    """Rebuild queue rows from seed overrides that already passed external verification."""
    seed_path = ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    clean_path = ROOT / "data" / "processed" / "smart_factories_clean.csv"
    if not seed_path.exists():
        return 0
    seed = pd.read_csv(seed_path)
    ext = seed[seed["resolution_class"].astype(str) == "external_evidence_verified"].copy()
    ext = ext[ext["external_evidence_url"].fillna("").astype(str).str.strip() != ""]
    if ext.empty:
        return 0
    clean = pd.read_csv(clean_path) if clean_path.exists() else pd.DataFrame()
    meta = (
        clean.set_index("project_id")[["firm_name_zh", "project_name_zh", "source_url"]]
        if not clean.empty and "firm_name_zh" in clean.columns
        else pd.DataFrame()
    )
    rows = []
    for rank, (_, row) in enumerate(ext.iterrows(), start=1):
        pid = row["project_id"]
        firm, project, src = "", "", ""
        if not meta.empty and pid in meta.index:
            firm = str(meta.loc[pid, "firm_name_zh"])
            project = str(meta.loc[pid, "project_name_zh"])
            src = str(meta.loc[pid, "source_url"])
        rows.append(
            {
                "priority_rank": rank,
                "project_id": pid,
                "firm_name_zh": firm,
                "project_name_zh": project,
                "city": row["city"],
                "province": row["province"],
                "resolution_class": "external_evidence_verified",
                "evidence_type": row.get("evidence_type", ""),
                "evidence_url": src,
                "priority_reason": "verified_external_seed",
                "external_evidence_url": row["external_evidence_url"],
                "external_evidence_type": row.get("evidence_type", "company_site_registry"),
                "audit_notes": str(row.get("notes", ""))[:500],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(QUEUE, index=False, encoding="utf-8-sig")
    return len(out)


def main() -> int:
    if not QUEUE.exists():
        print(f"Missing {QUEUE}")
        return 1
    research: dict[str, dict[str, str]] = dict(B2_SUPPLEMENT)
    for doc in DOCS:
        research.update(parse_research_rows(doc))
    queue = pd.read_csv(QUEUE)
    filled = 0
    for idx, row in queue.iterrows():
        pid = str(row["project_id"])
        existing = row.get("external_evidence_url", "")
        if pd.notna(existing) and str(existing).strip() and str(existing).strip().lower() != "nan":
            continue
        hit = research.get(pid)
        if not hit:
            continue
        for k, v in hit.items():
            queue.at[idx, k] = v
        filled += 1
    for col in ("external_evidence_url", "external_evidence_type", "audit_notes"):
        queue[col] = queue[col].astype("object")
    queue.to_csv(QUEUE, index=False, encoding="utf-8-sig")
    n_url = int(queue["external_evidence_url"].fillna("").astype(str).str.strip().ne("").sum())
    print(f"Applied research URLs to {filled} queue rows in {QUEUE}")
    if n_url < 50:
        synced = sync_queue_from_verified_seed()
        if synced:
            queue = pd.read_csv(QUEUE)
            n_url = int(queue["external_evidence_url"].fillna("").astype(str).str.strip().ne("").sum())
            print(f"Synced {synced} verified rows from seed overrides into queue")
    print(f"Queue rows with external_evidence_url: {n_url}/{len(queue)}")
    return 0 if n_url >= 50 else 1


if __name__ == "__main__":
    raise SystemExit(main())
