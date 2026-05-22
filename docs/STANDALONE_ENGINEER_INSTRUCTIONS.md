# Standalone Engineer Instructions

**Current sprint (2026-05-22):** Workstream A is closed on the public path (Table I appendix only; strict Table 5 skipped). **Critical path: B1 audit + B2 external verification.** See [`docs/CURRENT_SPRINT_PRIORITIES.md`](CURRENT_SPRINT_PRIORITIES.md).

These instructions are written so each engineer can start without additional context.

## Project context for everyone

We are building a reproducible empirical pipeline for a research paper titled “The Diffusion State: China’s AI Industrialization Model and the Next Productivity Shock.” The paper studies whether China has a distinctive capacity to diffuse AI into industrial production through policy, local implementation, smart factories, industrial internet infrastructure, procurement, and export-oriented manufacturing.

The core empirical pipeline is narrow:

1. Identify Chinese cities designated as National New Generation AI Innovation and Development Pilot Zones.
2. Compile official excellence-level smart-factory projects as a measure of industrial AI adoption.
3. Aggregate smart-factory adoption to city-year and city-industry-year panels.
4. Link adoption to city controls and export outcomes.
5. Produce descriptive and quasi-experimental evidence suitable for an NBER-style paper.

The project is not trying to measure all Chinese AI activity. It is trying to measure a specific institutional mechanism: state-guided AI diffusion into industry.

## Shared setup instructions

Clone the repository.

```bash
git clone https://github.com/fraware/ai_diffusion_state.git
cd ai_diffusion_state
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make test
```

If `pip install -e .[dev]` fails because the scaffold has not yet been pushed, create the repo structure from the scaffold package and then retry.

Expected structure:

```text
configs/
data/
  raw/
  interim/
  processed/
docs/
notebooks/
outputs/
  figures/
  tables/
scripts/
src/diffusion_state/
tests/
```

Never commit large proprietary data. Keep raw downloaded files in `data/raw` locally unless the file is small, public, and explicitly allowed.

## Engineer A — Source acquisition and provenance

### Mission

Own source discovery, raw file acquisition, source registry maintenance, and provenance. Your work makes the entire project auditable.

### Core responsibilities

1. Maintain `configs/sources.yml`.
2. Download or preserve raw source pages and attachments.
3. Save raw files under `data/raw/<source_name>/`.
4. Create source notes in `docs/source_notes/`.
5. Ensure every downstream table can trace each row to a URL, attachment, or source file.

### Mandatory sources

1. CSET/MOST AI pilot-zone source.
2. Official MOST or government pages for AI pilot-zone guidance.
3. Official or mirrored MIIT excellence-level smart-factory lists.
4. BACI download page and metadata.
5. EPS or NBS city-statistics source notes.

### File outputs

Create or update:

```text
configs/sources.yml
data/raw/pilot_zones/
data/raw/smart_factories/
data/raw/baci/
data/raw/city_controls/
docs/source_notes/pilot_zones.md
docs/source_notes/smart_factories.md
docs/source_notes/baci.md
docs/source_notes/city_controls.md
```

### Provenance schema

Each source entry must include:

```yaml
source_id:
  name:
  source_type: official | mirror | academic | commercial | manual_seed
  url:
  accessed_at:
  expected_format: html | pdf | xlsx | csv | zip
  license_or_terms:
  local_path:
  notes:
```

### Acceptance criteria

Your work is done when another engineer can run the fetch script and recover the same raw files or see exactly where manual access is required. Every raw source must have a note explaining its origin, reliability, and limitations.

### Red flags to escalate

- A source has disappeared or changed content.
- A mirrored list conflicts with an official list.
- A list count differs from the official count.
- An attachment is a scanned image or otherwise not machine-readable.
- A source requires login or commercial access.

## Engineer B — Smart-factory parser and adoption tables

### Mission

Own the transformation from raw smart-factory lists into clean project-level, city-year, and city-industry-year adoption datasets.

### Input files

You depend on Engineer A for raw files in:

```text
data/raw/smart_factories/
```

You also depend on:

```text
configs/keywords_zh.yml
configs/city_aliases.yml
configs/industry_mapping.yml
```

If alias or mapping files do not exist, create them.

### Required output files

```text
data/interim/smart_factories_2024_raw.csv
data/interim/smart_factories_2025_raw.csv
data/processed/smart_factories_clean.csv
data/processed/smart_factory_city_year.csv
data/processed/smart_factory_city_industry_year.csv
data/processed/smart_factory_scenario_year.csv
```

### Project-level schema

`smart_factories_clean.csv` must contain:

```text
project_id
list_year
batch
firm_name_zh
firm_name_en
project_name_zh
project_name_en
province
city
city_confidence
industry_code
industry_label
industry_confidence
ai_scenario_tags
technology_tags
source_url
source_file
row_number_original
parse_method
manual_override_flag
notes
```

### AI scenario tags

Use Chinese keywords to identify tags such as:

- machine_vision
- ai_quality_inspection
- predictive_maintenance
- digital_twin
- intelligent_scheduling
- industrial_robotics
- smart_logistics
- industrial_internet
- ai_server
- semiconductor
- battery
- new_energy_vehicle
- steel
- petrochemical
- shipbuilding
- pharmaceutical

Scenario tags can be multiple. Keep them as a pipe-separated string or a normalized long table.

### City inference rules

Use this hierarchy:

1. Explicit city in project name.
2. Explicit city in firm name.
3. Official local government repost naming the city.
4. Firm registry or official company website.
5. Province-only assignment with `city = unknown`.

Never silently fill city from headquarters if the factory location may differ. If headquarters is used, set `city_confidence = low` and document the reason.

### Aggregation rules

`smart_factory_city_year.csv` should include:

```text
city
year
smart_factory_projects
smart_factory_projects_ai_tagged
smart_factory_projects_industrial_ai
num_distinct_firms
num_distinct_industries
source_rows
```

`smart_factory_city_industry_year.csv` should include:

```text
city
industry_code
year
smart_factory_projects
smart_factory_projects_ai_tagged
num_distinct_firms
source_rows
```

### Acceptance criteria

Your work is done when:

1. Project-level rows reconcile exactly to the raw lists used.
2. Required columns are non-null where logically required.
3. Aggregated tables reconcile to project-level totals.
4. At least 85 percent of rows have city confidence `medium` or above, or a memo explains why this target is unrealistic.
5. Tests cover required columns, uniqueness of project IDs, aggregation reconciliation, and scenario-tag validity.

## Engineer C — BACI trade and export-upgrading module

### Mission

Own the export-outcome side of the paper. Convert BACI raw data into China HS6-year and sector-year export outcomes that can be linked to smart-factory adoption.

### Input files

Raw BACI files should be placed in:

```text
data/raw/baci/
```

Use HS17 for 2017–2024 unless the research lead requests a different HS vintage.

### Required output files

```text
data/interim/baci_china_hs6_year.csv
data/processed/export_outcomes_hs6_year.csv
data/processed/export_outcomes_sector_year.csv
data/processed/hs_to_smart_factory_sector_bridge.csv
docs/source_notes/baci.md
```

### HS6-year schema

`export_outcomes_hs6_year.csv` must contain:

```text
year
hs6
export_value_usd
quantity
unit
unit_value
export_value_growth
quantity_growth
unit_value_growth
num_destinations
world_export_value_usd
china_world_market_share
```

### Sector-year schema

`export_outcomes_sector_year.csv` must contain:

```text
year
sector_code
sector_label
export_value_usd
quantity_available_share
unit_value_index
export_value_growth
unit_value_growth
china_world_market_share
hs6_count
mapping_confidence_summary
```

### Bridge file requirements

Create a documented bridge from smart-factory industry labels to HS sections, HS2, HS4, or HS6 families. Every mapping must include:

```text
smart_factory_industry_label
hs_level
hs_code
hs_description
mapping_confidence
mapping_reason
```

### Rules

1. Do not drop zero or missing quantities without documenting the reason.
2. Unit value equals export value divided by quantity only when quantity is positive and unit is comparable.
3. Export growth should use log differences where possible.
4. Keep raw-derived and cleaned/winsorized versions separate.
5. Do not mix HS vintages in the same output file unless a concordance is explicitly applied.

### Acceptance criteria

Your work is done when:

1. China HS6 exports are available for all target years.
2. Unit values are computed with documented missingness.
3. Sector bridge covers at least the main smart-factory sectors: vehicles, batteries, semiconductors, steel, shipbuilding, petrochemicals, industrial machinery, electronics, pharmaceuticals, robotics, and AI servers.
4. Tests validate no negative values, no duplicate HS6-year rows, and stable totals across aggregation levels.

## Engineer D — City controls, panel construction, and econometrics

### Mission

Own the construction of the final analysis panels and the first regression outputs.

### Inputs

You depend on:

```text
data/processed/pilot_zones.csv
data/processed/smart_factories_clean.csv
data/processed/smart_factory_city_year.csv
data/processed/smart_factory_city_industry_year.csv
data/processed/export_outcomes_sector_year.csv
data/processed/city_controls_year.csv
```

### Required output files

```text
data/processed/analysis_city_year_panel.csv
data/processed/analysis_city_industry_year_panel.csv
outputs/tables/table_1_dataset_summary.csv
outputs/tables/table_2_top_smart_factory_cities.csv
outputs/tables/table_3_pilot_zone_adoption_models.csv
outputs/tables/table_4_export_upgrading_models.csv
outputs/figures/fig_event_study_pilot_zones.png
docs/analysis_memo_v1.md
docs/red_team_memo.md
```

### Panel schemas

`analysis_city_year_panel.csv` must contain:

```text
city
province
year
pilot_zone
pilot_year
post_pilot
years_since_pilot
smart_factory_projects
smart_factory_projects_ai_tagged
gdp
gdp_per_capita
industrial_output
secondary_value_added
population
wages
fdi
fixed_asset_investment
telecom_or_internet_proxy
foreign_trade
```

`analysis_city_industry_year_panel.csv` must contain:

```text
city
province
industry_code
industry_label
year
pilot_zone
pilot_year
post_pilot
years_since_pilot
smart_factory_projects
smart_factory_projects_ai_tagged
ai_exposure_industry
export_value_growth
unit_value_growth
city_controls
```

### Baseline analyses

Run four outputs.

1. Dataset summary table.
2. Top smart-factory cities and pilot-zone overlap.
3. City-year adoption model.
4. City-industry adoption model with AI-exposure interaction.

Suggested model progression:

```text
Model 1: smart_factory_projects_ct ~ pilot_zone_c + year FE
Model 2: smart_factory_projects_ct ~ post_pilot_ct + city FE + year FE
Model 3: smart_factory_projects_ct ~ post_pilot_ct + city FE + province-year FE + controls
Model 4: smart_factory_projects_cit ~ post_pilot_ct * ai_exposure_i + city-industry FE + year FE
```

Use Poisson or negative binomial models for count outcomes if OLS is unstable. Keep OLS/log(1+y) versions for interpretability.

### Event-study requirements

Create event time:

```text
event_time = year - pilot_year
```

Use bins:

```text
<= -4, -3, -2, -1, 0, 1, 2, 3, >= 4
```

Omit `-1` as the reference year. Report pre-trend coefficients clearly.

### Interpretation rules

Do not claim the pilot zones caused productivity growth unless the evidence supports it. The honest interpretation should be:

- First result: pilot-zone cities have higher observed adoption of official smart-factory projects.
- Stronger result if event study works: adoption accelerates after designation relative to pre-trends.
- Strongest result if interaction works: adoption rises especially in AI-exposed industrial sectors.
- Export results are suggestive unless the mapping and timing are strong.

### Acceptance criteria

Your work is done when:

1. A fresh run reproduces every table and figure.
2. Models run without manual notebook intervention.
3. The analysis memo explains what can and cannot be inferred.
4. The red-team memo identifies selection, pre-trends, measurement bias, and mapping uncertainty.

## Engineer E — Paper production and research QA, if available

### Mission

Own the bridge from data outputs to paper evidence. Your job is to make sure the empirical pipeline produces defensible research claims.

### Required outputs

```text
paper/outline.md
paper/introduction_claims.md
paper/data_appendix.md
paper/results_narrative.md
paper/limitations.md
```

### Core questions to answer

1. What does the dataset measure well?
2. What does it fail to measure?
3. Which claims are descriptive?
4. Which claims are quasi-causal?
5. Which claims must be framed as suggestive?
6. Which results would convince a skeptical NBER reviewer?

### Acceptance criteria

Your work is done when every major paper claim has an associated table, figure, data source, or caveat.

## Communication protocol

Each engineer should post a daily update with:

1. What changed.
2. What files were added or modified.
3. What validation passed.
4. What is blocked.
5. What decision is needed from the research lead.

PRs should be small. Do not bundle unrelated data sources. A parser PR should not also add regression results.

## Final standard

The final repo should make the following command sequence possible:

```bash
make fetch
make build
make test
make analysis
make outputs
```

The result should be a complete audit trail from raw source to paper table.
