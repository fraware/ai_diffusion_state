from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

MAIN_TABLES = PROJECT_ROOT / "paper" / "main_tables"
TABLES_MD = PROJECT_ROOT / "paper" / "tables_md"
MANIFEST_PATH = PROJECT_ROOT / "paper" / "table_manifest.json"
CLAIM_MAP = PROJECT_ROOT / "paper" / "main_table_claim_map.csv"

MAX_FULL_ROWS = 40


@dataclass(frozen=True)
class TableSpec:
    file_name: str
    label: str
    caption: str
    placement: str  # main | appendix
    claim_id: str
    claim_tier: str


TABLE_SPECS: tuple[TableSpec, ...] = (
    TableSpec(
        "table_A_dataset_counts.csv",
        "Table A",
        "Dataset counts and coverage (pilot zones, smart-factory projects, geo evidence classes).",
        "main",
        "measurement_pilot_zones",
        "measured",
    ),
    TableSpec(
        "table_B_city_resolution_quality.csv",
        "Table B",
        "City-resolution evidence quality by resolution class and evidence type.",
        "main",
        "geo_resolution_quality",
        "validated_descriptive",
    ),
    TableSpec(
        "table_C_pilot_overlap.csv",
        "Table C",
        "Pilot-zone vs non-pilot overlap in listed smart-factory projects (resolved cities).",
        "main",
        "descriptive_pilot_overlap",
        "validated_descriptive",
    ),
    TableSpec(
        "table_D_hub_exclusion.csv",
        "Table D",
        "Hub-exclusion robustness for pilot-zone association in city-year adoption models.",
        "main",
        "hub_robustness",
        "robust_association",
    ),
    TableSpec(
        "table_E_city_typology.csv",
        "Table E",
        "City diffusion typology — project counts by type (outcome-informed labels; descriptive).",
        "main",
        "hub_architecture_typology",
        "validated_descriptive",
    ),
    TableSpec(
        "table_E_ex_ante_city_typology.csv",
        "Table E (ex ante)",
        "Ex ante city capacity typology — project counts by type (pre-outcome labels).",
        "main",
        "hub_architecture_typology_ex_ante",
        "validated_descriptive",
    ),
    TableSpec(
        "table_F_ex_ante_industry_heterogeneity.csv",
        "Table F",
        "City-industry adoption models — key terms only (ex ante exposure interactions).",
        "main",
        "city_industry_exposure_ex_ante",
        "suggestive_mechanism",
    ),
    TableSpec(
        "table_G_export_relevance.csv",
        "Table G",
        "Export relevance of smart-factory sectors (descriptive).",
        "main",
        "export_relevance_descriptive",
        "validated_descriptive",
    ),
    TableSpec(
        "table_H_export_sector_share_comparison.csv",
        "Table H",
        "Listed smart-factory sectors vs 2024 export basket shares (descriptive).",
        "main",
        "export_sector_share_comparison",
        "validated_descriptive",
    ),
    TableSpec(
        "table_I_appendix_public_fallback_controls.csv",
        "Table I",
        "Appendix: partial 2024 ChinaUTC public controls (not EPS-equivalent).",
        "appendix",
        "appendix_public_fallback_controls",
        "partial_public_controls_appendix_only",
    ),
)


def _is_fe_term(term: str) -> bool:
    return bool(re.match(r"^C\((city|industry_code|year)\)", str(term)))


def _prepare_dataframe(spec: TableSpec, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    note = ""
    if spec.file_name == "table_E_city_typology.csv":
        col = "diffusion_type" if "diffusion_type" in df.columns else df.columns[-1]
        df = (
            df.groupby(col, as_index=False)["resolved_smart_factory_projects"]
            .sum()
            .sort_values("resolved_smart_factory_projects", ascending=False)
        )
        note = "Aggregated from city-level typology file."
    elif spec.file_name == "table_E_ex_ante_city_typology.csv":
        col = "diffusion_type_ex_ante"
        df = (
            df.groupby(col, as_index=False)
            .size()
            .rename(columns={"size": "n_cities"})
            .sort_values("n_cities", ascending=False)
        )
        note = "City counts by ex ante typology (not project-weighted)."
    elif spec.file_name == "table_F_ex_ante_industry_heterogeneity.csv":
        df = df[~df["term"].map(_is_fe_term)].copy()
        keep_models = [
            "city_industry_pilot_x_exposure_ex_ante",
            "city_industry_pilot_x_score_ex_ante",
            "city_industry_pilot_x_exposure_tag_descriptive",
        ]
        df = df[df["model"].isin(keep_models)]
        cols = [c for c in ["model", "term", "coef", "std_err", "p_value", "n_obs", "exposure_source"] if c in df.columns]
        df = df[cols]
        note = "FE coefficients omitted; tag-derived spec is descriptive-only (not for main causal claims)."
    elif spec.file_name == "table_I_appendix_public_fallback_controls.csv":
        df = df[df["term"] == "pilot_zone"].copy()
        note = "Pilot-zone rows only (appendix robustness)."
    elif len(df) > MAX_FULL_ROWS:
        df = df.head(MAX_FULL_ROWS)
        note = f"First {MAX_FULL_ROWS} rows shown; full table in paper/main_tables/{spec.file_name}."

    return df, note


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    try:
        return df.to_markdown(index=False)
    except ImportError:
        return df.to_string(index=False)


def build_paper_tables_md() -> list[dict]:
    TABLES_MD.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    claim_rows = pd.read_csv(CLAIM_MAP) if CLAIM_MAP.exists() else pd.DataFrame()
    claim_by_table = (
        claim_rows.groupby("paper_table").first().to_dict("index") if not claim_rows.empty else {}
    )

    for spec in TABLE_SPECS:
        src = MAIN_TABLES / spec.file_name
        status = "missing"
        md_path = TABLES_MD / spec.file_name.replace(".csv", ".md")
        row_count = 0
        note = ""

        if src.exists():
            df = pd.read_csv(src)
            row_count = len(df)
            df_out, note = _prepare_dataframe(spec, df)
            cm = claim_by_table.get(spec.file_name, {})
            claim_id = cm.get("claim_id", spec.claim_id) if isinstance(cm, dict) else spec.claim_id
            claim_tier = cm.get("claim_tier", spec.claim_tier) if isinstance(cm, dict) else spec.claim_tier

            lines = [
                f"### {spec.label}",
                "",
                f"*{spec.caption}*",
                "",
                f"**Claim tier:** `{claim_tier}` | **Claim ID:** `{claim_id}` | **Placement:** {spec.placement}",
                "",
            ]
            if note:
                lines.append(f"*Note: {note}*")
                lines.append("")
            lines.append(_dataframe_to_markdown(df_out))
            lines.append("")
            lines.append(f"Source: `paper/main_tables/{spec.file_name}` ({row_count} rows in repository).")
            lines.append("")
            md_path.write_text("\n".join(lines), encoding="utf-8")
            status = "built"

        manifest.append(
            {
                "paper_table": spec.file_name,
                "label": spec.label,
                "markdown_path": f"paper/tables_md/{md_path.name}",
                "claim_id": spec.claim_id,
                "claim_tier": spec.claim_tier,
                "placement": spec.placement,
                "caption": spec.caption,
                "source_rows": row_count,
                "status": status,
            }
        )

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"tables": manifest}, f, indent=2)
    return manifest


def tables_markdown_section() -> str:
    """Concatenate all table markdown files for submission draft."""
    if not MANIFEST_PATH.exists():
        build_paper_tables_md()
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    lines = ["## Tables (paper/main_tables)", ""]
    lines.append(
        "Embedded from reproducible CSVs. Claim tiers follow `paper/main_table_claim_map.csv`. "
        "Table I is appendix-only and not EPS-equivalent."
    )
    lines.append("")
    main = [t for t in data["tables"] if t.get("placement") == "main" and t.get("status") == "built"]
    appendix = [t for t in data["tables"] if t.get("placement") == "appendix" and t.get("status") == "built"]

    lines.append("### Main text tables")
    lines.append("")
    for entry in main:
        md_rel = entry["markdown_path"].replace("paper/", "")
        body = (PROJECT_ROOT / entry["markdown_path"]).read_text(encoding="utf-8")
        lines.append(body)

    if appendix:
        lines.append("### Appendix tables")
        lines.append("")
        for entry in appendix:
            body = (PROJECT_ROOT / entry["markdown_path"]).read_text(encoding="utf-8")
            lines.append(body)

    return "\n".join(lines)
