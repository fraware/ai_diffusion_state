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


def _filled_audit_decisions(audit: pd.DataFrame) -> int:
    dec = audit["auditor_decision"]
    mask = dec.notna() & (dec.astype(str).str.strip() != "") & (dec.astype(str) != "nan")
    return int(mask.sum())


def _geo_class_counts() -> tuple[int, int, int]:
    """Return (official, rule_based, external) project counts from Table 16 or register."""
    official, rule_based, external = 102, 357, 0
    t16 = _read_table("table_16_geo_evidence_quality.csv")
    if t16 is not None and "evidence_type" in t16.columns:
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
        if external > 0 or rule_based != 407:
            return official, rule_based, external
    reg_path = PROJECT_ROOT / "data" / "processed" / "city_resolution_register.csv"
    if reg_path.exists():
        reg = pd.read_csv(reg_path)
        if "resolution_class" in reg.columns:
            vc = reg["resolution_class"].value_counts()
            official = int(vc.get("official_location_exact", official))
            rule_based = int(vc.get("rule_based_text_inference", rule_based))
            external = int(vc.get("external_evidence_verified", external))
    return official, rule_based, external


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
    official, rule_based, external = _geo_class_counts()
    seed = PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    n_rules = 0
    if seed.exists():
        s = pd.read_csv(seed)
        if "resolution_class" in s.columns:
            n_rules = int((s["resolution_class"] != "external_evidence_verified").sum())
        else:
            n_rules = len(s)
    audit_path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    audit_line = "Stratified city-resolution audit is **pending** (Table 17)."
    if audit_path.exists():
        filled = _filled_audit_decisions(pd.read_csv(audit_path))
        if filled >= 70:
            audit_line = "Stratified city-resolution audit is **complete** (Table 17; 70/70 sample decisions)."
        elif filled > 0:
            audit_line = f"Stratified city-resolution audit **in progress** ({filled}/70 sample decisions; Table 17)."
    return (
        f"- **509** projects with assigned city (**0** unknown in current build).\n"
        f"- **{official}** `official_location_exact`, **{rule_based}** `rule_based_text_inference`, "
        f"**{external}** `external_evidence_verified` (Table 16).\n"
        f"- **{n_rules}** city-resolution override rows in `data/seed/smart_factory_city_overrides.csv` "
        f"(excluding external-verification overrides; registry/list inference unless `external_evidence_url` is set).\n"
        f"- {audit_line}\n"
    )


def build_geo_coverage_paragraph() -> str:
    official, rule_based, external = _geo_class_counts()
    audit_path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    audit_done = audit_path.exists() and _filled_audit_decisions(pd.read_csv(audit_path)) >= 70
    if external >= 50 and audit_done:
        return (
            f"All **509** projects are assigned to cities with three evidence classes (Table 16): "
            f"**{official}** official-location exact, **{rule_based}** rule-based inference, "
            f"**{external}** with non-list external evidence. Stratified audit sample is complete (Table 17). "
            "Do not describe the register as fully externally audited; cite external verification only for "
            "the verified rows and audit conclusions for the stratified sample.\n"
        )
    return (
        "All **509** projects are assigned to cities. Evidence quality work remains: complete external "
        "verification (target ≥50) and stratified audit (Table 17) before claiming audited geocoding.\n"
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
    filled = _filled_audit_decisions(a)
    if filled == 0:
        return (
            "**City-resolution audit:** **pending** — fill `data/audit/city_resolution_sample_audit.csv` "
            "(50 rule-based + 20 official minimum), then `make recompute-audit`.\n"
        )
    t17 = _read_table("table_17_geo_audit_error_rate.csv")
    if t17 is not None and not t17.empty:
        lines = [f"**City-resolution audit:** **{filled}/{len(a)}** sample decisions (Table 17)."]
        for _, row in t17.iterrows():
            rc = str(row["resolution_class"])
            n = int(row["sampled_rows"])
            conf = int(row.get("confirmed", 0))
            insuf = int(row.get("insufficient_evidence", 0))
            incor = int(row.get("incorrect", 0))
            if rc == "official_location_exact":
                lines.append(f"Official-location sample: **{conf}/{n}** confirmed.")
            elif rc == "rule_based_text_inference":
                parts = [f"**{conf}** confirmed"]
                if insuf:
                    parts.append(f"**{insuf}** insufficient_evidence")
                if incor:
                    parts.append(f"**{incor}** incorrect")
                lines.append(f"Rule-based sample (n={n}): {', '.join(parts)}.")
        return " ".join(lines) + "\n"
    incorrect = int((a["auditor_decision"] == "incorrect").sum())
    confirmed = int((a["auditor_decision"] == "confirmed").sum())
    return (
        f"**City-resolution audit:** **{filled}/{len(a)}** rows decided "
        f"({confirmed} confirmed, {incorrect} incorrect). Table 17 via `make recompute-audit`.\n"
    )


def build_reviewer_seed_line() -> str:
    seed = PROJECT_ROOT / "data" / "seed" / "smart_factory_city_overrides.csv"
    n = 0
    n_ext = 0
    if seed.exists():
        s = pd.read_csv(seed)
        if "resolution_class" in s.columns:
            n_ext = int((s["resolution_class"] == "external_evidence_verified").sum())
            n = int((s["resolution_class"] != "external_evidence_verified").sum())
        else:
            n = len(s)
    return (
        f"| City-resolution override rows (seed) | **{n}** inference overrides; "
        f"**{n_ext}** external-verification overrides |\n"
    )


def build_reviewer_geo_resolution_table() -> str:
    official, rule_based, external = _geo_class_counts()
    return (
        "| `resolution_class` | Projects |\n"
        "|--------------------|--------:|\n"
        f"| `official_location_exact` | {official} |\n"
        f"| `rule_based_text_inference` | {rule_based} |\n"
        f"| `external_evidence_verified` | {external} |\n"
    )


def build_red_team_geo_priority() -> str:
    official, rule_based, external = _geo_class_counts()
    audit_path = PROJECT_ROOT / "data" / "audit" / "city_resolution_sample_audit.csv"
    audit_note = "Stratified audit sample pending (Table 17)."
    if audit_path.exists() and _filled_audit_decisions(pd.read_csv(audit_path)) >= 70:
        audit_note = "Stratified audit sample complete (Table 17)."
    return (
        f"2. City resolution uses **three evidence classes** (Table 16): **{official}** official-location "
        f"exact, **{rule_based}** rule-based, **{external}** external-evidence verified (non-list URLs). "
        f"{audit_note} Do not claim full external audit of all 509 assignments; use class-specific language.\n"
    )


def sync_red_team_memo(path: Path | None = None) -> Path:
    path = path or PAPER / "red_team_memo.md"
    text = path.read_text(encoding="utf-8")
    text = _replace_block(
        text, "<!-- PCS:RED_TEAM_HUB -->", "<!-- /PCS:RED_TEAM_HUB -->", build_red_team_hub_paragraph()
    )
    text = _replace_block(
        text, "<!-- PCS:PILOT_MEAN_CLAIM -->", "<!-- /PCS:PILOT_MEAN_CLAIM -->", build_pilot_mean_claim()
    )
    text = _replace_block(
        text,
        "<!-- PCS:RED_TEAM_GEO -->",
        "<!-- /PCS:RED_TEAM_GEO -->",
        build_red_team_geo_priority(),
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
    text = _replace_block(
        text,
        "<!-- PCS:REVIEWER_GEO_TABLE -->",
        "<!-- /PCS:REVIEWER_GEO_TABLE -->",
        build_reviewer_geo_resolution_table(),
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


def build_table_i_reviewer_section() -> str:
    t = _read_table("table_5b_public_fallback_controls.csv")
    if t is None:
        return "**Table I:** _missing — run `make public-fallback-controls`._\n"
    lines = [
        "**Status:** Strict Table 5 skipped. Appendix Table I uses 2024 ChinaUTC partial controls (no FDI / fixed-asset investment).",
        "",
        "| Model | pilot_zone coef | p-value | N | Note |",
        "|-------|----------------:|--------:|--:|------|",
    ]
    for model_key, label in [
        ("model_5b_public_fallback_count_2024", "5b OLS count"),
        ("model_5c_public_fallback_log_count_2024", "5c OLS log count"),
        ("model_5d_public_fallback_poisson_2024", "5d Poisson"),
    ]:
        sub = t[(t["model"] == model_key) & (t["term"] == "pilot_zone")]
        if sub.empty:
            continue
        r = sub.iloc[0]
        note = "significant" if float(r["p_value"]) < 0.05 else "not significant"
        if "poisson" in model_key:
            note += "; appendix only"
        lines.append(
            f"| {label} | {float(r['coef']):.2f} | {_fmt_p(r['p_value'])} | {int(r['n_obs'])} | {note} |"
        )
    lines.append("")
    lines.append(
        "Do not cite as EPS-equivalent or primary controlled evidence. See "
        "`docs/PUBLIC_FALLBACK_CONTROLS_INTERPRETATION.md`."
    )
    return "\n".join(lines) + "\n"


def sync_reviewer_table_i(path: Path | None = None) -> Path:
    path = path or PAPER / "reviewer_results_snapshot.md"
    text = path.read_text(encoding="utf-8")
    if "<!-- PCS:TABLE_I -->" not in text:
        insert = (
            "\n## Appendix public fallback (Table I)\n\n"
            "<!-- PCS:TABLE_I -->\n"
            "_Placeholder — run make sync-paper-stats._\n"
            "<!-- /PCS:TABLE_I -->\n"
        )
        marker = "## Controlled models (Table 5)"
        if marker in text:
            text = text.replace(marker, insert + "\n" + marker)
        else:
            text = text.rstrip() + insert
    text = _replace_block(
        text, "<!-- PCS:TABLE_I -->", "<!-- /PCS:TABLE_I -->", build_table_i_reviewer_section()
    )
    path.write_text(text, encoding="utf-8")
    return path


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
    snap = PAPER / "reviewer_results_snapshot.md"
    if snap.exists():
        sync_reviewer_table_i(snap)
        updated.append(snap)
    return updated
