from __future__ import annotations

from dataclasses import dataclass

from diffusion_state.utils import PROJECT_ROOT, normalize_cn_text, read_yaml


@dataclass(frozen=True)
class TagResult:
    ai_scenario_tags: str
    technology_tags: str
    has_industrial_ai_keyword: bool
    industry_code: str
    industry_label: str
    industry_confidence: str


GENERIC_FACTORY_KEYWORDS = frozenset({"智能工厂", "智能制造", "数字化车间"})


def _collect_keywords() -> list[str]:
    cfg = read_yaml(PROJECT_ROOT / "configs" / "keywords_zh.yml")
    keywords: list[str] = []
    for group in cfg.get("industrial_ai_keywords", {}).values():
        keywords.extend(group)
    return keywords


def _scenario_tags(text: str) -> list[str]:
    rules = read_yaml(PROJECT_ROOT / "configs" / "scenario_tag_rules.yml").get("rules", [])
    hits: list[str] = []
    text_n = normalize_cn_text(text)
    for rule in rules:
        if any(k in text_n for k in rule.get("keywords", [])):
            hits.extend(rule.get("tags", []))
    return sorted(set(hits))


def _industry_assignment(text: str) -> tuple[str, str, str]:
    cfg = read_yaml(PROJECT_ROOT / "configs" / "industry_mapping.yml")
    text_n = normalize_cn_text(text)
    for rule in cfg.get("rules", []):
        if any(p in text_n for p in rule.get("patterns", [])):
            return (
                rule["industry_code"],
                rule["industry_label"],
                "high",
            )
    default = cfg.get("default", {})
    return (
        default.get("industry_code", "C34"),
        default.get("industry_label", "general_equipment"),
        default.get("industry_confidence", "low"),
    )


def tag_project(firm_name_zh: str, project_name_zh: str) -> TagResult:
    text = f"{firm_name_zh} {project_name_zh}"
    text_n = normalize_cn_text(text)
    industrial_keywords = _collect_keywords()
    tech_hits = [
        k for k in industrial_keywords if k in text_n and k not in GENERIC_FACTORY_KEYWORDS
    ]
    scenario = _scenario_tags(text)
    industry_code, industry_label, industry_confidence = _industry_assignment(text)
    return TagResult(
        ai_scenario_tags="|".join(scenario),
        technology_tags="|".join(tech_hits),
        has_industrial_ai_keyword=bool(tech_hits),
        industry_code=industry_code,
        industry_label=industry_label,
        industry_confidence=industry_confidence,
    )
