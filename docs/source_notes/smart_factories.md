# Excellence-level smart factories — source notes

## Purpose

Firm/project-level adoption measure from MIIT **卓越级智能工厂** public lists (2024 first batch, 2025 batch).

## Raw sources (committed workflow: download locally, never edit)

| Batch | File | URL | Official count |
|---|---|---|---|
| 2024 first batch | `data/raw/smart_factories/2024_mirror.html` | https://cn.solarbe.com/news/20250103/92225.html | 235 |
| 2025 batch | `data/raw/smart_factories/2025_jlts.html` | https://jlts.com.cn/i/news/detail/2571072131159669662.html | 274 |

Official MIIT notice (2024): https://www.ncsti.gov.cn/kjdt/tzgg/202501/t20250103_191636.html

## Parse methods

- **2024:** One HTML `<p>` per row: `rank firm project location` (regex-validated; must equal 235).
- **2025:** Embedded `<table>` inside article HTML; columns 序号 / 企业名称 / 项目名称 / 所在地 (must equal 274).

## Outputs

| File | Rows expected |
|---|---|
| `data/interim/smart_factories_2024_raw.csv` | 235 |
| `data/interim/smart_factories_2025_raw.csv` | 274 |
| `data/processed/smart_factories_clean.csv` | 509 |
| `data/processed/smart_factory_city_year.csv` | city-year aggregates (excludes `city=unknown`) |
| `data/processed/smart_factory_city_industry_year.csv` | city-industry-year aggregates |

## City and industry fields

- `city` / `province` from `configs/province_normalization.yml` and explicit `XX市` in firm/project text.
- `city_confidence`: `exact` (municipality or location city), `high` (city from firm parenthetical, prefix, or text), `unknown` (province-only location in source).
- **Geo coverage:** run `python scripts/report_smart_factory_geo.py` after each parse. Province-only `项目所在地` (e.g. `江苏省`) remains `city=unknown` by design.
- **2024 parse method:** `html_p_tag_rtl_location` — location token at end of line; firm matched on legal suffix (`股份有限公司`, etc.) so project names may include `AI` tokens.
- `ai_scenario_tags` from `configs/scenario_tag_rules.yml` + `configs/keywords_zh.yml`.
- `industry_code` / `industry_label` from first match in `configs/industry_mapping.yml`.

## Reproducibility

```bash
# Requires raw HTML in data/raw/smart_factories/
python scripts/02_parse_smart_factories.py
make test
```

Manual corrections: add rows to `data/seed/smart_factory_city_overrides.csv` (required columns: `project_id`, `city`, `province`, `city_confidence`, `override_source`, `notes`). Rebuild with `make build`. Do not edit generated CSVs.
