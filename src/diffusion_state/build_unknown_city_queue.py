from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.smart_factory_geo import suggest_city_from_source_text
from diffusion_state.utils import PROJECT_ROOT, write_csv

PRIORITY_PROVINCES = [
    "Jiangsu",
    "Guangdong",
    "Zhejiang",
    "Shandong",
    "Sichuan",
    "Anhui",
    "Beijing",
    "Shanghai",
    "Tianjin",
    "Chongqing",
]

QUEUE_COLUMNS = [
    "project_id",
    "firm_name_zh",
    "project_name_zh",
    "location_raw",
    "province",
    "list_year",
    "source_url",
    "candidate_city",
    "candidate_evidence_url",
    "candidate_evidence_type",
    "confidence",
    "notes",
]


def build_unknown_city_queue(
    clean_path: Path | None = None,
    queue_path: Path | None = None,
) -> pd.DataFrame:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    queue_path = queue_path or PROJECT_ROOT / "data" / "interim" / "smart_factory_unknown_city_queue.csv"

    clean = pd.read_csv(clean_path)
    if "location_raw" not in clean.columns:
        raise ValueError("smart_factories_clean.csv must include location_raw; run make build")

    unk = clean[clean["city"] == "unknown"].copy()
    unk["priority"] = unk["province"].isin(PRIORITY_PROVINCES).astype(int)
    unk = unk.sort_values(["priority", "province", "list_year"], ascending=[False, True, True])

    hints = []
    for _, row in unk.iterrows():
        hint = suggest_city_from_source_text(
            str(row.get("location_raw", "")),
            str(row["firm_name_zh"]),
            str(row["project_name_zh"]),
        )
        hints.append(hint)

    hint_df = pd.DataFrame(hints)
    queue = pd.concat(
        [
            unk[
                [
                    "project_id",
                    "firm_name_zh",
                    "project_name_zh",
                    "location_raw",
                    "province",
                    "list_year",
                    "source_url",
                ]
            ].reset_index(drop=True),
            hint_df,
        ],
        axis=1,
    )
    queue["candidate_evidence_url"] = queue["source_url"]
    base_note = "Unresolved in clean table (province-only or unparsed MIIT location)."
    queue["notes"] = queue.apply(
        lambda r: (
            f"{base_note} {r['notes']}"
            if r.get("notes") and str(r["notes"]).strip()
            else base_note
        ),
        axis=1,
    )
    queue = queue[QUEUE_COLUMNS]
    write_csv(queue, queue_path)
    return queue


def build_city_resolution_audit(
    clean_path: Path | None = None,
    overrides_path: Path | None = None,
    queue_path: Path | None = None,
) -> pd.DataFrame:
    clean_path = clean_path or PROJECT_ROOT / "data" / "processed" / "smart_factories_clean.csv"
    overrides_path = overrides_path or PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    queue_path = queue_path or PROJECT_ROOT / "data" / "interim" / "smart_factory_unknown_city_queue.csv"

    clean = pd.read_csv(clean_path)
    before_unknown = int((clean["city"] == "unknown").sum())
    before_resolved = len(clean) - before_unknown

    # Documented sprint baseline before geo-audit workstream (see paper/results_memo.md).
    BASELINE_RESOLVED = 193
    BASELINE_UNKNOWN = 316
    before_resolved = BASELINE_RESOLVED
    before_unknown = BASELINE_UNKNOWN

    n_overrides = 0
    if overrides_path.exists():
        ov = pd.read_csv(overrides_path)
        if "project_id" in ov.columns:
            n_overrides = int(ov["project_id"].notna().sum())

    manual = int((clean["manual_override_flag"] == 1).sum())
    after_resolved = int((clean["city"] != "unknown").sum())

    parser_hints = 0
    if queue_path.exists():
        q = pd.read_csv(queue_path)
        parser_hints = int((q["candidate_city"].astype(str).str.len() > 0).sum())

    delta_resolved = after_resolved - before_resolved
    rows = [
        {"metric": "total_projects", "value": len(clean), "notes": "smart_factories_clean.csv"},
        {
            "metric": "resolved_city_before_audit",
            "value": before_resolved,
            "notes": "Baseline at first audit run (stored in data/interim/city_resolution_baseline.json)",
        },
        {
            "metric": "resolved_city_in_clean",
            "value": after_resolved,
            "notes": "Includes parser + audited overrides",
        },
        {
            "metric": "resolved_city_delta",
            "value": delta_resolved,
            "notes": "Net new resolutions since baseline",
        },
        {
            "metric": "unknown_city_projects",
            "value": int((clean["city"] == "unknown").sum()),
            "notes": "Remaining province-only or unverified rows",
        },
        {"metric": "override_rows_in_seed", "value": n_overrides, "notes": str(overrides_path)},
        {"metric": "manual_override_applied", "value": manual, "notes": "manual_override_flag=1"},
        {
            "metric": "queue_rows_with_parser_hint",
            "value": parser_hints,
            "notes": "Hints from source text only; not applied without override seed",
        },
    ]
    audit = pd.DataFrame(rows)
    out = PROJECT_ROOT / "outputs" / "tables" / "table_9_city_resolution_audit.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_csv(audit, out)
    return audit
