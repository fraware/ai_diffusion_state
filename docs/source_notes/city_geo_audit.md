# City geo audit workstream

## Purpose

Resolve province-only MIIT smart-factory list locations to prefecture-level cities using **auditable evidence**, not headquarters-only guessing.

## Commands

```bash
make geo-audit          # overrides seed + rebuild clean + panel
make panel analysis     # downstream tables
```

`scripts/10_build_audited_city_overrides.py` runs three steps:

1. Rebuild `smart_factories_clean.csv` with audited resolver in `resolve_geo`.
2. Write `data/seed/smart_factory_city_overrides.csv` for inferable rows (evidence columns required).
3. Rebuild clean applying overrides.

## Evidence hierarchy

Allowed automatic evidence (`audited_city_resolution.py`):

| Type | Example |
|------|---------|
| `miit_location_field` | Location string is `深圳市` |
| `firm_province_county` | `福建省晋江市` in legal name |
| `firm_parenthetical` | `信义节能玻璃（芜湖）有限公司` |
| `firm_embedded_city_token` | `徐州重型机械`, `宁德新能源` |
| `project_branch_city` | `广州分公司` in project title |
| Registry match | Curated `configs/audited_firm_city_registry.yml` |

Blocked: province-only firm prefix without plant token (e.g. `广东` + national brand with no city token).

## Configuration

- `configs/city_geo_tokens.yml` — Chinese place tokens in firm/project text
- `configs/city_locality_aliases.yml` — branch/subsidiary locality aliases (e.g. 金陵 → Nanjing)
- `configs/audited_firm_city_registry.yml` — curated firm substring → city
- `configs/audited_firm_city_registry_supplement.yml` — generated plant-city supplement (`scripts/11_build_registry_supplement.py`)

`resolve_cn_locality()` in `smart_factory_geo.py` unifies parenthetical, branch, and token resolution.

## Outputs

- `data/seed/smart_factory_city_overrides.csv` — auditable override seed (committed when updated)
- `outputs/tables/table_9_city_resolution_audit.csv` — before/after metrics (baseline 193 resolved; v2 build **503** resolved)
- `data/interim/smart_factory_unknown_city_queue.csv` — manual review queue (**6** rows after v2 pass)

## Evidence classes (`resolution_class`)

| Class | Meaning | `evidence_url` |
|-------|---------|----------------|
| `official_location_exact` | MIIT location field names the city | Smart-factory list page OK |
| `rule_based_text_inference` | City from list text, registry plant map, tokens, branches | List page only |
| `external_evidence_verified` | External URL proves plant city | Must not be list-page URL |

Hygiene check: `make validate-geo` or `scripts/13_validate_geo_evidence.py`.

Paper wording: “503 projects are city-resolved: X official-location, Y rule-based inference, Z externally verified” (from Table 16 `_all` rows).

Regenerate supplement before geo-audit when adding plant maps:

```bash
py -3 scripts/11_build_registry_supplement.py
make geo-audit
make validate-geo
```

## City controls (CI)

`make city-controls-stub` installs synthetic controls for pipeline verification only. Paper claims require EPS/NBS via `make city-controls`.
