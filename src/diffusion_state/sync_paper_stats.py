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


def sync_results_memo(path: Path | None = None) -> Path:
    path = path or PAPER / "results_memo.md"
    text = path.read_text(encoding="utf-8")
    text = _replace_block(text, "<!-- PCS:OVERLAP_TABLE -->", "<!-- /PCS:OVERLAP_TABLE -->", build_overlap_markdown())
    text = _replace_block(
        text, "<!-- PCS:HUB_TABLE -->", "<!-- /PCS:HUB_TABLE -->", build_hub_exclusion_markdown()
    )
    text = _replace_block(text, "<!-- PCS:MODEL1 -->", "<!-- /PCS:MODEL1 -->", build_model1_line())
    path.write_text(text, encoding="utf-8")
    return path


def sync_reviewer_snapshot(path: Path | None = None) -> Path:
    path = path or PAPER / "reviewer_results_snapshot.md"
    text = path.read_text(encoding="utf-8")
    text = _replace_block(
        text, "<!-- PCS:REVIEWER_HUB -->", "<!-- /PCS:REVIEWER_HUB -->", build_reviewer_hub_lines()
    )
    t3 = _read_table("table_3_pilot_zone_adoption_models.csv")
    n_cities = "?"
    if t3 is not None:
        m1 = t3[t3["model"].astype(str).str.contains("model_1", na=False) & (t3["term"] == "pilot_zone")]
        if not m1.empty and "n_cities" in m1.columns:
            n_cities = str(int(m1.iloc[0]["n_cities"]))
    line = f"| Cities in adoption panel | **{n_cities}** (pilot + smart-factory universe) |\n"
    text = _replace_block(text, "<!-- PCS:ADOPTION_CITIES -->", "<!-- /PCS:ADOPTION_CITIES -->", line)
    path.write_text(text, encoding="utf-8")
    return path


def sync_all() -> list[Path]:
    updated = []
    for rel in ("results_memo.md", "reviewer_results_snapshot.md"):
        target = PAPER / rel
        if not target.exists():
            continue
        if rel == "results_memo.md":
            sync_results_memo(target)
        else:
            sync_reviewer_snapshot(target)
        updated.append(target)
    return updated
