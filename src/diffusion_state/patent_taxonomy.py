from __future__ import annotations

from dataclasses import dataclass

from diffusion_state.utils import PROJECT_ROOT, contains_any, normalize_cn_text, read_yaml

TAXONOMY_PATH = PROJECT_ROOT / "configs" / "patent_taxonomy.yml"

CATEGORY_COLUMNS = [
    "machine_vision",
    "robotics",
    "predictive_maintenance",
    "digital_twin",
    "quality_inspection",
    "industrial_scheduling",
    "process_control",
    "smart_logistics",
    "industrial_software",
    "industrial_foundation_model",
    "semiconductor_manufacturing_ai",
    "battery_manufacturing_ai",
    "chemical_process_ai",
]


@dataclass(frozen=True)
class PatentClassification:
    is_industrial_ai: bool
    is_excluded_non_industrial: bool
    categories: dict[str, bool]
    classification_source: str


def _load_taxonomy() -> dict:
    return read_yaml(TAXONOMY_PATH)


def _text_or_empty(value: str | None) -> str:
    if value is None:
        return ""
    try:
        import pandas as pd

        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value)


def _combined_text(
    title: str | None,
    abstract: str | None,
    claims_or_description: str | None,
    ipc_or_cpc: str | None,
) -> str:
    parts = [
        _text_or_empty(title),
        _text_or_empty(abstract),
        _text_or_empty(claims_or_description),
        _text_or_empty(ipc_or_cpc),
    ]
    return normalize_cn_text(" ".join(parts))


def classify_patent_text(
    title: str | None = None,
    abstract: str | None = None,
    claims_or_description: str | None = None,
    ipc_or_cpc: str | None = None,
    cset_row: dict | None = None,
) -> PatentClassification:
    """Classify a patent into industrial AI taxonomy categories."""
    cfg = _load_taxonomy()
    text = _combined_text(title, abstract, claims_or_description, ipc_or_cpc)

    exclusions = []
    for group in cfg.get("non_industrial_exclusions", {}).values():
        exclusions.extend(group)
    is_excluded = contains_any(text, exclusions) if text else False

    categories: dict[str, bool] = {c: False for c in CATEGORY_COLUMNS}
    source = "keywords"

    for cat, spec in cfg.get("categories", {}).items():
        keywords = spec.get("keywords", [])
        if text and contains_any(text, keywords):
            categories[cat] = True

    if cset_row:
        for field, cat in cfg.get("cset_field_map", {}).items():
            if cset_row.get(field) in (True, "True", 1, "1"):
                if cat in categories:
                    categories[cat] = True
                    source = "cset_fields+keywords" if any(categories.values()) else "cset_fields"

    is_industrial = any(categories.values()) and not is_excluded
    return PatentClassification(
        is_industrial_ai=is_industrial,
        is_excluded_non_industrial=is_excluded,
        categories=categories,
        classification_source=source,
    )


def category_count_columns() -> list[str]:
    return [f"{c}_patents" for c in CATEGORY_COLUMNS]
