.PHONY: setup seed fetch build parse baci panel analysis paper outputs test all clean

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e .[dev]

# Seed tables from manually verified CSVs (no network required)
seed:
	$(PYTHON) scripts/00_build_seed_tables.py

# Download or snapshot public source pages listed in configs/sources.yml
fetch:
	$(PYTHON) scripts/01_fetch_source_pages.py

# Analysis-ready processed tables from seeds and parsed smart-factory HTML
build: seed parse

parse:
	$(PYTHON) scripts/02_parse_smart_factories.py

baci:
	$(PYTHON) scripts/03_build_baci_outcomes.py

city-controls:
	$(PYTHON) scripts/06_build_city_controls.py

panel: build
	$(PYTHON) scripts/04_build_city_year_panel.py

analysis: panel
	$(PYTHON) scripts/05_run_baseline_models.py

outputs: analysis

paper: analysis
	$(PYTHON) scripts/07_build_paper_bundle.py

test:
	pytest -q

all: build baci panel analysis paper test

clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; \
	[shutil.rmtree(p, ignore_errors=True) for p in ['data/interim','data/processed','outputs']]; \
	[Path(d).mkdir(parents=True, exist_ok=True) for d in ['data/interim','data/processed','outputs/tables','outputs/figures']]"
