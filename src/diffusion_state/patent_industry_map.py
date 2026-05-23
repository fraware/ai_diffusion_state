from __future__ import annotations

import re

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, contains_any, normalize_cn_text, read_yaml

CROSSWALK_PATH = PROJECT_ROOT / "data" / "seed" / "industry_crosswalk_atlas.csv"
INDUSTRY_MAPPING_PATH = PROJECT_ROOT / "configs" / "industry_mapping.yml"


def load_industry_crosswalk() -> pd.DataFrame:
    if not CROSSWALK_PATH.exists():
        raise FileNotFoundError(f"Atlas industry crosswalk missing: {CROSSWALK_PATH}")
    return pd.read_csv(CROSSWALK_PATH)


def _ipc_prefix(ipc_or_cpc: str | None) -> str:
    if ipc_or_cpc is None or (isinstance(ipc_or_cpc, float) and pd.isna(ipc_or_cpc)):
        return ""
    text = str(ipc_or_cpc).strip().upper()
    m = re.match(r"([A-H]\d{2})", text)
    return m.group(1) if m else ""


def map_patent_industry(
    title: str | None = None,
    abstract: str | None = None,
    applicant_name: str | None = None,
    ipc_or_cpc: str | None = None,
) -> tuple[str, str, str, str]:
    """Return industry_code, industry_label, confidence, mapping_reason."""
    crosswalk = load_industry_crosswalk()
    text = normalize_cn_text(
        " ".join(
            [
                str(title or ""),
                str(abstract or ""),
                str(applicant_name or ""),
            ]
        )
    )
    ipc_prefix = _ipc_prefix(ipc_or_cpc)

    for _, row in crosswalk.iterrows():
        prefixes = str(row.get("ipc_prefixes", "")).split(",")
        prefixes = [p.strip() for p in prefixes if p.strip()]
        if ipc_prefix and any(ipc_prefix.startswith(p) for p in prefixes):
            conf = str(row.get("mapping_confidence_default", "medium"))
            label = row.get("industry", row.get("industry_label", row["industry_code"]))
            return (
                row["industry_code"],
                str(label),
                conf,
                f"ipc_prefix:{ipc_prefix}",
            )

    for _, row in crosswalk.iterrows():
        patterns = str(row.get("keyword_patterns", "")).split(",")
        patterns = [p.strip() for p in patterns if p.strip()]
        if text and contains_any(text, patterns):
            conf = str(row.get("mapping_confidence_default", "medium"))
            label = row.get("industry", row.get("industry_label", row["industry_code"]))
            return (
                row["industry_code"],
                str(label),
                conf,
                "keyword_crosswalk",
            )

    cfg = read_yaml(INDUSTRY_MAPPING_PATH)
    for rule in cfg.get("rules", []):
        if any(p in text for p in rule.get("patterns", [])):
            return (
                rule["industry_code"],
                rule["industry_label"],
                "high",
                "industry_mapping_yml",
            )

    default = cfg.get("default", {})
    return (
        default.get("industry_code", "C34"),
        default.get("industry_label", "general_equipment"),
        default.get("industry_confidence", "low"),
        "default_rule",
    )
