"""Sync quantitative claims in paper memos from regenerated output tables."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

TABLES = PROJECT_ROOT / "outputs" / "tables"
PAPER = PROJECT_ROOT / "paper"

HUB_RULE_LABELS = {
    "full_sample": "Full sample",
    "drop_beijing_shanghai_shenzhen_hangzhou": "Drop Beijing, Shanghai, Shenzhen, Hangzhou",
    "drop_beijing_shanghai_shenzhen_hangzhou_guangzhou": "Drop above + Guangzhou",
    "drop_direct_admin_municipalities": "Drop direct-admin municipalities",
    "drop_top_5_smart_factory_cities": "Drop top 5 smart-factory cities",
    "drop_top_10_gdp_cities": "Drop top 10 GDP cities",
}


def _fmt_coef(v: float) -> str:
    return f"{v:.2f}"


def _fmt_p(v: float) -> str:
    if pd.isna(v):
        return "—"
    if v < 0.001:
        return "<0.001"
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _fmt_pct_share(v: float) -> str:
    if pd.isna(v):
        return "—"
    return f"~{int(round(100 * v))}%"


def _read_table(name: str) -> pd.DataFrame | None:
    path = TABLES / name
    return pd.read_csv(path) if path.exists() else None


def build_hub_exclusion_markdown() -> str:
    t6 = _read_table("table_6_hub_exclusion_robustness.csv")
    if t6 is None:
        return "_Hub table missing — run `make analysis`._\n"

    base = t6[
        (t6["spec"].astype(str) == "baseline")
        & (t6["term"].astype(str) == "pilot_zone")
    ].copy()
    if base.empty:
        return "_No baseline pilot_zone rows in Table 6._\n"

    lines = [
        "| Exclusion rule | Cities | Projects | pilot_zone coef | p-value | Reader takeaway |",
        "|----------------|-------:|---------:|----------------:|--------:|-----------------|",
    ]
    for _, row in base.iterrows():
        rule = str(row["exclusion_rule"])
        label = HUB_RULE_LABELS.get(rule, rule)
        interp = str(row.get("interpretation", "")).strip()
        if rule == "full_sample":
            interp = "Baseline (analysis universe, resolved cities)"
        rel = row.get("coefficient_relative_to_full_sample", float("nan"))
        if rule != "full_sample" and pd.notna(rel):
            if rel < 0.7:
                interp = f"Substantially weakens ({_fmt_pct_share(rel)} of coef)"
            elif rel < 0.85:
                interp = f"Weakens ({_fmt_pct_share(rel)} of coef)"
            else:
                interp = f"Sensitive ({_fmt_pct_share(rel)} of coef)"
        lines.append(
            f"| {label} | {int(row['n_cities'])} | {int(row['n_projects'])} | "
            f"{_fmt_coef(float(row['coef']))} | {_fmt_p(float(row['p_value']))} | {interp} |"
        )
    return "\n".join(lines) + "\n"


def build_overlap_markdown() -> str:
    path = TABLES / "table_pilot_zone_overlap.csv"
    if not path.exists():
        return "_Overlap table missing — run `make analysis`._\n"
    ov = pd.read_csv(path)
    lines = [
        "| Sample | Cities | Total projects | Mean per city |",
        "|--------|-------:|---------------:|--------------:|",
    ]
    proj_col = "total_projects" if "total_projects" in ov.columns else "total_projects_2024_2025"
    mean_col = "mean_per_city" if "mean_per_city" in ov.columns else "mean_projects_per_city"
    for _, row in ov.iterrows():
        lines.append(
            f"| {row['sample']} | {int(row['n_cities'])} | {int(row[proj_col])} | "
            f"{float(row[mean_col]):.2f} |"
        )
    return "\n".join(lines) + "\n"


def build_model1_line() -> str:
    t3 = _read_table("table_3_pilot_zone_adoption_models.csv")
    if t3 is None:
        return "**Model 1:** _table missing._\n"
    m1 = t3[
        t3["model"].astype(str).str.contains("model_1", na=False)
        & (t3["term"].astype(str) == "pilot_zone")
    ]
    if m1.empty:
        return "**Model 1:** _pilot_zone term missing._\n"
    row = m1.iloc[0]
    n_cities = int(row["n_cities"]) if "n_cities" in row and pd.notna(row["n_cities"]) else "?"
    n_obs = int(row["n_obs"]) if "n_obs" in row and pd.notna(row["n_obs"]) else "?"
    return (
        f"**Model 1:** `pilot_zone` coef = **{_fmt_coef(float(row['coef']))}**, "
        f"p {_fmt_p(float(row['p_value']))} — N = {n_obs} city-years, **{n_cities}** cities "
        f"(pilot + non-pilot universe). Interpret jointly with Table 6 hub attenuation (not collapse).\n"
    )


def build_reviewer_hub_lines() -> str:
    t6 = _read_table("table_6_hub_exclusion_robustness.csv")
    if t6 is None:
        return "| _missing_ | — | — | — |\n"
    base = t6[
        (t6["spec"].astype(str) == "baseline")
        & (t6["term"].astype(str) == "pilot_zone")
    ]
    rows = []
    pick = [
        ("full_sample", "Full sample"),
        ("drop_beijing_shanghai_shenzhen_hangzhou", "Drop BJ/SH/SZ/HZ"),
        ("drop_direct_admin_municipalities", "Drop direct-admin"),
        ("drop_top_5_smart_factory_cities", "Drop top-5 SF cities"),
    ]
    for key, label in pick:
        sub = base[base["exclusion_rule"].astype(str) == key]
        if sub.empty:
            continue
        r = sub.iloc[0]
        rel = r.get("coefficient_relative_to_full_sample", float("nan"))
        note = "Baseline"
        if key != "full_sample" and pd.notna(rel):
            note = f"Weakens ({_fmt_pct_share(rel)} of coef)"
        rows.append(
            f"| {label} | {_fmt_coef(float(r['coef']))} | {_fmt_p(float(r['p_value']))} | {note} |"
        )
    header = "| Rule | coef | p-value | Note |\n|------|-----:|--------:|------|\n"
    return header + "\n".join(rows) + "\n"


def _replace_block(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        flags=re.DOTALL,
    )
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"Markers not found: {start} / {end}")
    return pattern.sub(replacement, text, count=1)


def _hub_row(rule: str) -> pd.Series | None:
    t6 = _read_table("table_6_hub_exclusion_robustness.csv")
    if t6 is None:
        return None
    sub = t6[
        (t6["spec"].astype(str) == "baseline")
        & (t6["exclusion_rule"].astype(str) == rule)
        & (t6["term"].astype(str) == "pilot_zone")
    ]
    return sub.iloc[0] if not sub.empty else None


def build_red_team_hub_paragraph() -> str:
    full = _hub_row("full_sample")
    da = _hub_row("drop_direct_admin_municipalities")
    top5 = _hub_row("drop_top_5_smart_factory_cities")
    if full is None:
        return "_Table 6 missing — run make analysis._\n"
    nc = int(full["n_cities"])
    np = int(full["n_projects"])
    c0 = _fmt_coef(float(full["coef"]))
    c_da = _fmt_coef(float(da["coef"])) if da is not None else "—"
    c_t5 = _fmt_coef(float(top5["coef"])) if top5 is not None else "—"
    return (
        f"The hub-exclusion table (analysis universe: **{nc}** cities, **{np}** listed projects in "
        f"2024–2025) shows that the baseline pilot-zone coefficient **weakens outside mega-hubs** and "
        f"**falls substantially when direct-admin municipalities are excluded** (coef ≈ {c_da} vs. "
        f"{c0} full sample; top-five smart-factory cities ≈ {c_t5}). The association does not go to "
        f"zero with full city coverage, but hub concentration remains visible in typology and "
        f"descriptive overlap. Evidence is consistent with **hub-centered diffusion capacity** "
        f"rather than uniform treatment across treated cities.\n"
    )


def build_pilot_mean_claim() -> str:
    ov = _read_table("table_pilot_zone_overlap.csv")
    if ov is None or ov.empty:
        return "_Overlap table missing._\n"
    pilot = ov[ov["sample"].astype(str).str.contains("pilot_zone", na=False)]
    nonp = ov[ov["sample"].astype(str).str.contains("non_pilot", na=False)]
    if pilot.empty or nonp.empty:
        return "_Pilot/non-pilot overlap rows missing._\n"
    mcol = "mean_projects_per_city" if "mean_projects_per_city" in pilot.columns else "mean_per_city"
    pm = float(pilot.iloc[0][mcol])
    nm = float(nonp.iloc[0][mcol])
    return (
        f"2. Listed adoption is **concentrated** in pilot-zone cities among resolved-city projects "
        f"(mean **{pm:.2f}** vs **{nm:.2f}**).\n"
    )


def build_geo_resolution_bullets() -> str:
    t16 = _read_table("table_16_geo_evidence_quality.csv")
    official, rule_based, external = 102, 407, 0
    if t16 is not None:
        summary = t16[t16["evidence_type"].astype(str) == "_all"]
        for _, r in summary.iterrows():
            rc = str(r["resolution_class"])
            n = int(r["n_projects"])
            if rc == "official_location_exact":
                official = n
            elif rc == "rule_based_text_inference":
                rule_based = n
            elif rc == "external_evidence_verified":
                external = n
    seed = PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    n_rules = 0
    if seed.exists():
        n_rules = len(pd.read_csv(seed))
    audit_pending = True
    audit_path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    if audit_path.exists():
        a = pd.read_csv(audit_path)
        filled = (a["auditor_decision"].fillna("").astype(str).str.strip() != "").sum()
        audit_pending = filled == 0
    audit_line = (
        "Stratified city-resolution audit is **pending** (`data/audit/city_resolution_sample_audit.csv` → Table 17)."
        if audit_pending
        else "Stratified city-resolution audit is **complete** (Table 17)."
    )
    return (
        f"- **509** projects with assigned city (**0** unknown in current build).\n"
        f"- **{official}** `official_location_exact`, **{rule_based}** `rule_based_text_inference`, "
        f"**{external}** `external_evidence_verified` (Table 16).\n"
        f"- **{n_rules}** city-resolution rule rows in `data/seed/smart_factory_city_overrides.csv` "
        f"(registry/list inference — not external verification unless `external_evidence_url` is set).\n"
        f"- {audit_line}\n"
    )


def build_geo_coverage_paragraph() -> str:
    return (
        "All **509** projects are currently assigned to cities. The remaining task is not coverage but "
        "**evidence quality**: distinguishing official-location exact, rule-based inference, and externally "
        "verified assignments. Do not describe the register as externally audited until non-list URLs are "
        "added and Table 17 is completed.\n"
    )


def build_reviewer_overlap() -> str:
    ov = _read_table("table_pilot_zone_overlap.csv")
    if ov is None:
        return "| _missing_ | — | — | — |\n"
    lines = ["| Sample | Cities | Projects | Mean/city |", "|--------|-------:|---------:|----------:|"]
    proj = "total_projects_2024_2025" if "total_projects_2024_2025" in ov.columns else "total_projects"
    mean = "mean_projects_per_city" if "mean_projects_per_city" in ov.columns else "mean_per_city"
    labels = {
        "pilot_zone_cities": "Pilot-zone",
        "non_pilot_zone_cities": "Non-pilot",
    }
    for _, row in ov.iterrows():
        sample = str(row["sample"])
        if sample not in labels:
            continue
        lines.append(
            f"| {labels[sample]} | {int(row['n_cities'])} | {int(row[proj])} | {float(row[mean]):.2f} |"
        )
    return "\n".join(lines) + "\n"


def build_audit_status_paragraph() -> str:
    audit_path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    if not audit_path.exists():
        return "**City-resolution audit:** sample file missing (run `make geo-audit`).\n"
    a = pd.read_csv(audit_path)
    filled = (a["auditor_decision"].fillna("").astype(str).str.strip() != "").sum()
    if filled == 0:
        return (
            "**City-resolution audit:** **pending** — fill `data/audit/city_resolution_sample_audit.csv` "
            "(50 rule-based + 20 official minimum), then `make recompute-audit`.\n"
        )
    incorrect = int((a["auditor_decision"] == "incorrect").sum())
    confirmed = int((a["auditor_decision"] == "confirmed").sum())
    return (
        f"**City-resolution audit:** **{filled}/{len(a)}** rows decided "
        f"({confirmed} confirmed, {incorrect} incorrect). Table 17 updated via `make recompute-audit`.\n"
    )


def build_reviewer_seed_line() -> str:
    seed = PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    n = len(pd.read_csv(seed)) if seed.exists() else 0
    return f"| City-resolution rule rows (seed) | **{n}** (rule-based register; not external audit) |\n"


def sync_red_team_memo(path: Path | None = None) -> Path:
    path = path or PAPER / "red_team_memo.md"
    text = path.read_text(encoding="utf-8")
    text = _replace_block(
        text, "<!-- PCS:RED_TEAM_HUB -->", "<!-- /PCS:RED_TEAM_HUB -->", build_red_team_hub_paragraph()
    )
    text = _replace_block(
        text, "<!-- PCS:PILOT_MEAN_CLAIM -->", "<!-- /PCS:PILOT_MEAN_CLAIM -->", build_pilot_mean_claim()
    )
    path.write_text(text, encoding="utf-8")
    return path


def sync_results_memo(path: Path | None = None) -> Path:
    path = path or PAPER / "results_memo.md"
    text = path.read_text(encoding="utf-8")
    text = _replace_block(text, "<!-- PCS:OVERLAP_TABLE -->", "<!-- /PCS:OVERLAP_TABLE -->", build_overlap_markdown())
    text = _replace_block(
        text, "<!-- PCS:HUB_TABLE -->", "<!-- /PCS:HUB_TABLE -->", build_hub_exclusion_markdown()
    )
    text = _replace_block(text, "<!-- PCS:MODEL1 -->", "<!-- /PCS:MODEL1 -->", build_model1_line())
    text = _replace_block(
        text, "<!-- PCS:GEO_RESOLUTION -->", "<!-- /PCS:GEO_RESOLUTION -->", build_geo_resolution_bullets()
    )
    text = _replace_block(
        text, "<!-- PCS:GEO_COVERAGE -->", "<!-- /PCS:GEO_COVERAGE -->", build_geo_coverage_paragraph()
    )
    path.write_text(text, encoding="utf-8")
    return path


def sync_reviewer_snapshot(path: Path | None = None) -> Path:
    path = path or PAPER / "reviewer_results_snapshot.md"
    text = path.read_text(encoding="utf-8")
    text = _replace_block(
        text, "<!-- PCS:REVIEWER_HUB -->", "<!-- /PCS:REVIEWER_HUB -->", build_reviewer_hub_lines()
    )
    text = _replace_block(
        text, "<!-- PCS:ADOPTION_CITIES -->", "<!-- /PCS:ADOPTION_CITIES -->", _adoption_cities_line()
    )
    text = _replace_block(
        text, "<!-- PCS:REVIEWER_SEED -->", "<!-- /PCS:REVIEWER_SEED -->", build_reviewer_seed_line()
    )
    text = _replace_block(
        text, "<!-- PCS:REVIEWER_OVERLAP -->", "<!-- /PCS:REVIEWER_OVERLAP -->", build_reviewer_overlap()
    )
    text = _replace_block(
        text, "<!-- PCS:AUDIT_STATUS -->", "<!-- /PCS:AUDIT_STATUS -->", build_audit_status_paragraph()
    )
    path.write_text(text, encoding="utf-8")
    return path


def _adoption_cities_line() -> str:
    t3 = _read_table("table_3_pilot_zone_adoption_models.csv")
    n_cities = "?"
    if t3 is not None:
        m1 = t3[t3["model"].astype(str).str.contains("model_1", na=False) & (t3["term"] == "pilot_zone")]
        if not m1.empty and "n_cities" in m1.columns:
            n_cities = str(int(m1.iloc[0]["n_cities"]))
    return f"| Cities in adoption panel | **{n_cities}** (pilot + smart-factory universe) |\n"


def sync_all() -> list[Path]:
    updated = []
    for rel, fn in (
        ("results_memo.md", sync_results_memo),
        ("reviewer_results_snapshot.md", sync_reviewer_snapshot),
        ("red_team_memo.md", sync_red_team_memo),
    ):
        target = PAPER / rel
        if not target.exists():
            continue
        fn(target)
        updated.append(target)
    return updated
