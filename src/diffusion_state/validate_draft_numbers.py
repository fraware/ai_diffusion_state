from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.sync_paper_stats import _geo_class_counts, _read_table
from diffusion_state.utils import PROJECT_ROOT

DRAFT_PATH = PROJECT_ROOT / "paper" / "draft_v1.md"
TOLERANCE = 0.06  # allow rounding in prose (e.g. 4.55 vs 4.5)


@dataclass(frozen=True)
class DraftNumberCheck:
    label: str
    expected: float
    pattern: str
    optional: bool = False


def _near(a: float, b: float, tol: float = TOLERANCE) -> bool:
    if pd.isna(a) or pd.isna(b):
        return False
    return abs(a - b) <= tol


def _extract_float(text: str, pattern: str) -> float | None:
    m = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not m:
        return None
    return float(m.group(1))


def build_expected_checks() -> list[DraftNumberCheck]:
    checks: list[DraftNumberCheck] = []

    t1 = _read_table("table_1_dataset_summary.csv")
    if t1 is not None:
        ds = t1["dataset"].astype(str)
        obs = t1["observations"].astype(float)
        pilots = t1[ds == "pilot_zones"]
        if not pilots.empty:
            checks.append(
                DraftNumberCheck(
                    "pilot_zone_units",
                    float(pilots.iloc[0]["observations"]),
                    r"(\d+)\s+AI pilot-zone units",
                )
            )
        sf = t1[ds == "smart_factories_clean"]
        if not sf.empty:
            checks.append(
                DraftNumberCheck(
                    "smart_factory_projects",
                    float(sf.iloc[0]["observations"]),
                    r"(\d+)\s+MIIT excellence-level smart-factory projects",
                )
            )

    official, rule_based, external = _geo_class_counts()
    checks.extend(
        [
            DraftNumberCheck("geo_official", official, r"(\d+)\s+projects are `official_location_exact`"),
            DraftNumberCheck("geo_rule_based", rule_based, r"(\d+)\s+are `rule_based_text_inference`"),
            DraftNumberCheck("geo_external", external, r"(\d+)\s+are `external_evidence_verified`"),
        ]
    )

    ov = _read_table("table_pilot_zone_overlap.csv")
    if ov is not None:
        pilot = ov[ov["sample"].astype(str) == "pilot_zone_cities"]
        nonp = ov[ov["sample"].astype(str) == "non_pilot_zone_cities"]
        proj_col = "total_projects_2024_2025" if "total_projects_2024_2025" in ov.columns else "total_projects"
        mean_col = "mean_projects_per_city" if "mean_projects_per_city" in ov.columns else "mean_per_city"
        if not pilot.empty:
            checks.append(
                DraftNumberCheck(
                    "pilot_projects",
                    float(pilot.iloc[0][proj_col]),
                    r"pilot-zone cities account for (\d+) listed",
                )
            )
            checks.append(
                DraftNumberCheck(
                    "pilot_mean",
                    float(pilot.iloc[0][mean_col]),
                    r"(\d+\.\d+)\s+per pilot-zone city",
                )
            )
        if not nonp.empty:
            checks.append(
                DraftNumberCheck(
                    "nonpilot_projects",
                    float(nonp.iloc[0][proj_col]),
                    r"non-pilot cities account for (\d+) projects",
                )
            )
            checks.append(
                DraftNumberCheck(
                    "nonpilot_mean",
                    float(nonp.iloc[0][mean_col]),
                    r"(\d+\.\d+)\s+per non-pilot city",
                )
            )

    t3 = _read_table("table_3_pilot_zone_adoption_models.csv")
    if t3 is not None:
        m1 = t3[
            t3["model"].astype(str).str.contains("model_1", na=False)
            & (t3["term"] == "pilot_zone")
        ]
        if not m1.empty:
            checks.append(
                DraftNumberCheck(
                    "baseline_pilot_coef",
                    float(m1.iloc[0]["coef"]),
                    r"pilot-zone coefficient is (\d+\.\d+)",
                )
            )

    t6 = _read_table("table_6_hub_exclusion_robustness.csv")
    if t6 is not None:
        base = t6[
            (t6["spec"] == "baseline")
            & (t6["exclusion_rule"] == "full_sample")
            & (t6["term"] == "pilot_zone")
        ]
        bj = t6[
            (t6["spec"] == "baseline")
            & (t6["exclusion_rule"] == "drop_beijing_shanghai_shenzhen_hangzhou")
            & (t6["term"] == "pilot_zone")
        ]
        da = t6[
            (t6["spec"] == "baseline")
            & (t6["exclusion_rule"] == "drop_direct_admin_municipalities")
            & (t6["term"] == "pilot_zone")
        ]
        t5 = t6[
            (t6["spec"] == "baseline")
            & (t6["exclusion_rule"] == "drop_top_5_smart_factory_cities")
            & (t6["term"] == "pilot_zone")
        ]
        if not base.empty and not bj.empty:
            checks.append(
                DraftNumberCheck(
                    "hub_drop_bjshzh",
                    float(bj.iloc[0]["coef"]),
                    r"Beijing, Shanghai, Shenzhen, and Hangzhou are removed, the (?:pilot-zone )?coefficient falls to (\d+\.\d+)",
                )
            )
        if not base.empty and not da.empty:
            checks.append(
                DraftNumberCheck(
                    "hub_drop_direct_admin",
                    float(da.iloc[0]["coef"]),
                    r"direct-admin municipalities are removed, the coefficient falls to (\d+\.\d+)",
                )
            )
        if not base.empty and not t5.empty:
            checks.append(
                DraftNumberCheck(
                    "hub_drop_top5_sf",
                    float(t5.iloc[0]["coef"]),
                    r"top five smart-factory cities are removed, it falls to (\d+\.\d+)",
                )
            )

    t5b = _read_table("table_5b_public_fallback_controls.csv")
    if t5b is not None:
        for model_suffix, pattern in [
            ("5b", r"OLS count coefficient is \+(\d+\.\d+)"),
            ("5c", r"OLS log-count coefficient is \+(\d+\.\d+)"),
        ]:
            sub = t5b[
                (t5b["term"] == "pilot_zone")
                & (t5b["model"].astype(str).str.contains(model_suffix, na=False))
            ]
            if not sub.empty:
                checks.append(
                    DraftNumberCheck(
                        f"table_i_{model_suffix}",
                        float(sub.iloc[0]["coef"]),
                        pattern,
                    )
                )

    return checks


def validate_draft_numbers(draft_path: Path | None = None) -> tuple[bool, list[str]]:
    draft_path = draft_path or DRAFT_PATH
    if not draft_path.exists():
        return False, [f"MISSING draft: {draft_path}"]

    text = draft_path.read_text(encoding="utf-8")
    issues: list[str] = []
    checks = build_expected_checks()

    for check in checks:
        found = _extract_float(text, check.pattern)
        if found is None:
            if not check.optional:
                issues.append(f"{check.label}: phrase not found in draft")
            continue
        if not _near(found, check.expected):
            issues.append(
                f"{check.label}: draft has {found}, tables imply {check.expected:.4f}"
            )

    return len(issues) == 0, issues
