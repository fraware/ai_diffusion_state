.PHONY: setup seed fetch build parse baci panel analysis paper validate-sprint outputs test all clean geo-audit purge-stub-controls production-check

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e .[dev]

# Seed tables from manually verified CSVs (no network required)
seed:
	$(PYTHON) scripts/00_build_seed_tables.py

# Download or snapshot public source pages listed in configs/sources.yml
fetch: setup
	$(PYTHON) scripts/01_fetch_source_pages.py

# Analysis-ready processed tables from seeds and parsed smart-factory HTML
build: setup seed parse

parse: setup
	$(PYTHON) scripts/02_parse_smart_factories.py

baci: setup
	$(PYTHON) scripts/03_build_baci_outcomes.py

city-controls: setup
	$(PYTHON) scripts/06_build_city_controls.py

validate-controls-raw: setup
	$(PYTHON) scripts/06a_validate_city_controls_raw.py

purge-stub-controls:
	$(PYTHON) scripts/22_purge_stub_controls.py

geo-audit: build
	$(PYTHON) scripts/11_build_registry_supplement.py
	$(PYTHON) scripts/10_build_audited_city_overrides.py
	$(PYTHON) scripts/04_build_city_year_panel.py

pcs: purge-stub-controls geo-audit panel analysis validate-geo validate-sprint main-tables sync-paper-stats paper test pcs-status

sync-paper-stats: analysis
	$(PYTHON) scripts/16_sync_paper_stats.py

production-check: setup
	$(PYTHON) scripts/17_validate_production_outputs.py

external-verification-queue: setup
	$(PYTHON) scripts/18_build_external_verification_queue.py

validate-audit: setup
	$(PYTHON) scripts/19_validate_audit_sample.py

apply-geo-updates: setup
	$(PYTHON) scripts/20_apply_geo_workflow_updates.py

preflight: purge-stub-controls
	$(PYTHON) scripts/21_pcs_preflight.py

pcs-status: setup
	$(PYTHON) scripts/15_pcs_status.py

panel: build
	$(PYTHON) scripts/04_build_city_year_panel.py

main-tables: analysis
	$(PYTHON) scripts/12_build_main_paper_tables.py

recompute-audit: setup
	$(PYTHON) scripts/14_recompute_geo_audit_error_rate.py

analysis: panel
	$(PYTHON) scripts/05_run_baseline_models.py

outputs: analysis

paper: analysis
	$(PYTHON) scripts/07_build_paper_bundle.py

validate-geo: setup
	$(PYTHON) scripts/13_validate_geo_evidence.py

validate-sprint: analysis
	$(PYTHON) scripts/13_validate_geo_evidence.py
	$(PYTHON) scripts/08_validate_sprint_outputs.py

test: setup
	pytest -q

all: setup build baci panel analysis paper test

clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; \
	[shutil.rmtree(p, ignore_errors=True) for p in ['data/interim','data/processed','outputs']]; \
	[Path(d).mkdir(parents=True, exist_ok=True) for d in ['data/interim','data/processed','outputs/tables','outputs/figures']]"
