"""Prioritize rule-based city assignments for external verification (Engineer B)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv

OUTPUT_PATH = PROJECT_ROOT / "data" / "interim" / "external_verification_queue.csv"
QUEUE_COLUMNS = [
    "priority_rank",
    "project_id",
    "firm_name_zh",
    "project_name_zh",
    "city",
    "province",
    "resolution_class",
    "evidence_type",
    "evidence_url",
    "priority_reason",
    "external_evidence_url",
    "external_evidence_type",
    "audit_notes",
]

ADVANCED_EXPORT_GROUPS = {
    "autos_and_nev",
    "batteries",
    "semiconductors_and_electronics",
    "ai_servers_and_computing_equipment",
    "shipbuilding",
    "steel_and_metals",
    "petrochemicals",
}


def _sector_group_map() -> dict[str, str]:
    from diffusion_state.build_export_revised import _sector_group_map as _map

    return _map()


def build_external_verification_queue(
    register_path: Path | None = None,
    clean_path: Path | None = None,
    target_n: int = 50,
    out_path: Path | None = None,
) -> pd.DataFrame:
    register_path = register_path or PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    out_path = out_path or OUTPUT_PATH

    if out_path.exists():
        prev = pd.read_csv(out_path)
        if "external_evidence_url" in prev.columns:
            urls = prev["external_evidence_url"]
            has_url = urls.notna() & (urls.astype(str).str.strip() != "") & (urls.astype(str) != "nan")
            if int(has_url.sum()) >= target_n:
                return prev

    if not register_path.exists():
        from diffusion_state.build_geo_evidence_quality import build_city_resolution_register

        build_city_resolution_register()

    reg = pd.read_csv(register_path)
    pool = reg[reg["resolution_class"] == "rule_based_text_inference"].copy()
    if pool.empty:
        out = pd.DataFrame(columns=QUEUE_COLUMNS)
        write_csv(out, out_path)
        return out

    clean = pd.read_csv(clean_path) if clean_path.exists() else pd.DataFrame()
    if not clean.empty and "industry_label" in clean.columns:
        group_map = _sector_group_map()
        clean = clean.assign(
            sector_group=lambda d: d["industry_label"].map(group_map).fillna("other")
        )
        pool = pool.merge(
            clean[["project_id", "industry_label", "sector_group"]],
            on="project_id",
            how="left",
        )
    else:
        pool["sector_group"] = "other"

    pilots = set()
    pz = PROJECT_ROOT / "data" / "processed" / "pilot_zones.csv"
    if pz.exists():
        pilots = set(pd.read_csv(pz)["city"])

    city_counts = (
        clean.groupby("city", as_index=False)["project_id"]
        .count()
        .rename(columns={"project_id": "city_project_count"})
        if not clean.empty
        else pd.DataFrame(columns=["city", "city_project_count"])
    )
    pool = pool.merge(city_counts, on="city", how="left")
    pool["city_project_count"] = pool["city_project_count"].fillna(0)

    top_cities = set()
    if not city_counts.empty:
        top_cities = set(city_counts.nlargest(20, "city_project_count")["city"])

    reasons: list[str] = []
    scores: list[int] = []
    for _, row in pool.iterrows():
        rs: list[str] = []
        score = 0
        if row["city"] in top_cities:
            rs.append("top_20_smart_factory_city")
            score += 4
        if row["city"] in pilots:
            rs.append("pilot_zone_city")
            score += 3
        if str(row.get("evidence_type", "")) == "firm_registry_match":
            rs.append("firm_registry_match")
            score += 2
        if str(row.get("sector_group", "")) in ADVANCED_EXPORT_GROUPS:
            rs.append("advanced_export_sector")
            score += 2
        if row["city_project_count"] >= 10:
            rs.append("high_city_project_count")
            score += 1
        reasons.append(";".join(rs) if rs else "rule_based_pool")
        scores.append(score)

    pool["priority_reason"] = reasons
    pool["priority_score"] = scores
    pool = pool.sort_values(["priority_score", "city_project_count"], ascending=[False, False])
    take = pool.head(target_n).copy()
    take["priority_rank"] = range(1, len(take) + 1)

    preserved: pd.DataFrame | None = None
    if out_path.exists():
        prev = pd.read_csv(out_path)
        keep = ["project_id", "external_evidence_url", "external_evidence_type", "audit_notes"]
        if all(c in prev.columns for c in keep):
            urls = prev["external_evidence_url"]
            has_url = urls.notna() & (urls.astype(str).str.strip() != "") & (urls.astype(str) != "nan")
            preserved = prev.loc[has_url, keep].drop_duplicates("project_id")

    out = pd.DataFrame(
        {
            "priority_rank": take["priority_rank"],
            "project_id": take["project_id"],
            "firm_name_zh": take.get("firm_name_zh", ""),
            "project_name_zh": take.get("project_name_zh", ""),
            "city": take["city"],
            "province": take["province"],
            "resolution_class": take["resolution_class"],
            "evidence_type": take["evidence_type"],
            "evidence_url": take.get("evidence_url", ""),
            "priority_reason": take["priority_reason"],
            "external_evidence_url": "",
            "external_evidence_type": "",
            "audit_notes": "",
        }
    )
    if preserved is not None and not preserved.empty:
        out = out.drop(columns=["external_evidence_url", "external_evidence_type", "audit_notes"]).merge(
            preserved,
            on="project_id",
            how="left",
        )
        for col in ("external_evidence_url", "external_evidence_type", "audit_notes"):
            out[col] = out[col].fillna("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(out, out_path)
    return out
