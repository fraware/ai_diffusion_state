.PHONY: setup seed fetch build parse baci panel analysis paper validate-sprint outputs test all clean geo-audit purge-stub-controls production-check public-fallback-controls patents atlas-exposure atlas-patents atlas-patent-prep atlas-patent-manifest atlas-iids-convert atlas-iids-geo atlas-iids-geo-validate atlas-iids-geo-build atlas-iids-pipeline atlas-iids-pipeline-full atlas-iids-preflight atlas-iids-smoke atlas-iids-manifest-merge atlas-iids-download-detail atlas-iids-export-keys atlas-iids-wsl-production atlas-iids-production-status atlas-iids-external-status atlas-iids-cloud atlas-iids-cloud-copyback atlas-iids-verify-copyback atlas-iids-import-copyback atlas-iids-geography-brief atlas-iids-control-post-copyback atlas-iids-control-evidence-chain atlas-iids-geo-fixture-smoke atlas-smartfactories atlas-sf-audit atlas-v02 atlas-models-v02 atlas-evidence-check atlas-status atlas-phase1 paper-figures paper-tables export-submission submission-bundle submission-zip submission-checklist validate-submission pcs-guard pcs-paper-owner cover-letter submission-docx

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
# (no setup: avoids pip rebuilding numpy on Windows when env is already installed)
build: seed parse

parse:
	$(PYTHON) scripts/02_parse_smart_factories.py

baci: setup
	$(PYTHON) scripts/03_build_baci_outcomes.py

city-controls:
	$(PYTHON) scripts/06_build_city_controls.py

validate-controls-raw:
	$(PYTHON) scripts/06a_validate_city_controls_raw.py

purge-stub-controls:
	$(PYTHON) scripts/22_purge_stub_controls.py

geo-audit: build
	$(PYTHON) scripts/11_build_registry_supplement.py
	$(PYTHON) scripts/10_build_audited_city_overrides.py
	$(PYTHON) scripts/04_build_city_year_panel.py

paper-figures: analysis
	$(PYTHON) scripts/34_build_paper_figures.py
	$(PYTHON) scripts/35_validate_paper_figures.py

paper-tables: main-tables
	$(PYTHON) scripts/38_build_paper_tables.py
	$(PYTHON) scripts/39_validate_paper_tables.py

export-submission: paper-figures paper-tables
	$(PYTHON) scripts/36_export_draft_submission.py

submission-bundle: export-submission
	$(PYTHON) scripts/51_build_submission_bundle.py

submission-checklist:
	$(PYTHON) scripts/52_build_submission_checklist.py

validate-submission: export-submission cover-letter submission-checklist submission-bundle submission-zip
	$(PYTHON) scripts/37_validate_submission_readiness.py

pcs: purge-stub-controls geo-audit panel analysis validate-geo public-fallback-controls main-tables sync-paper-stats production-check validate-draft paper-figures export-submission cover-letter submission-checklist submission-bundle submission-zip validate-submission validate-sprint validate-audit paper test pcs-status

sync-paper-stats: analysis
	$(PYTHON) scripts/16_sync_paper_stats.py

production-check:
	$(PYTHON) scripts/17_validate_production_outputs.py

external-verification-queue:
	$(PYTHON) scripts/18_build_external_verification_queue.py

validate-audit:
	$(PYTHON) scripts/19_validate_audit_sample.py

apply-geo-updates:
	$(PYTHON) scripts/20_apply_geo_workflow_updates.py

preflight: purge-stub-controls
	$(PYTHON) scripts/21_pcs_preflight.py

pcs-status:
	$(PYTHON) scripts/15_pcs_status.py --json

pcs-guard: pcs-status

pcs-paper-owner: pcs-guard cover-letter submission-checklist submission-bundle submission-zip validate-submission pcs-status
	@echo "Paper owner brief: paper/SUBMISSION_OWNER_BRIEF.md"

cover-letter:
	$(PYTHON) scripts/53_generate_cover_letter.py

submission-docx:
	$(PYTHON) scripts/42_export_submission_pandoc.py

submission-zip:
	$(PYTHON) scripts/54_build_submission_zip.py

validate-draft:
	$(PYTHON) scripts/33_validate_draft_numbers.py

panel: build
	$(PYTHON) scripts/04_build_city_year_panel.py

main-tables: analysis
	$(PYTHON) scripts/12_build_main_paper_tables.py

recompute-audit:
	$(PYTHON) scripts/14_recompute_geo_audit_error_rate.py

analysis: panel
	$(PYTHON) scripts/05_run_baseline_models.py

public-fallback-controls: panel
	$(PYTHON) scripts/28_run_public_fallback_controls.py

outputs: analysis

paper: analysis
	$(PYTHON) scripts/07_build_paper_bundle.py

validate-geo:
	$(PYTHON) scripts/13_validate_geo_evidence.py

validate-sprint: analysis
	$(PYTHON) scripts/13_validate_geo_evidence.py
	$(PYTHON) scripts/08_validate_sprint_outputs.py

patents:
	$(PYTHON) scripts/30_build_industrial_ai_patents.py
	$(PYTHON) scripts/31_validate_patent_layer.py

atlas-exposure:
	$(PYTHON) scripts/40_build_industry_exposure_v2.py
	$(PYTHON) scripts/41_validate_industry_exposure_v2.py

atlas-patents:
	$(PYTHON) scripts/42_parse_industrial_ai_patents.py
	$(PYTHON) scripts/43_build_industrial_ai_patents_city_industry_year.py
	$(PYTHON) scripts/44_validate_industrial_ai_patents.py

atlas-smartfactories:
	$(PYTHON) scripts/45_build_smart_factory_city_industry_year.py
	$(PYTHON) scripts/46_validate_smart_factory_city_industry_year.py

atlas-sf-audit:
	$(PYTHON) scripts/56_build_smart_factory_atlas_audit.py

atlas-evidence-check:
	$(PYTHON) scripts/55_validate_no_fixture_patents.py --json
	$(PYTHON) scripts/57_validate_patent_source_manifest.py

atlas-patent-manifest:
	$(PYTHON) scripts/57_validate_patent_source_manifest.py

atlas-patent-prep:
	$(PYTHON) scripts/58_prepare_patent_source_manifest.py

atlas-iids-convert:
	$(PYTHON) scripts/61_iids_sql_to_patent_csv.py

atlas-iids-geo:
	$(PYTHON) scripts/62_join_iids_patent_geography.py

atlas-iids-geo-validate:
	$(PYTHON) scripts/63_validate_patent_geography_supplement.py

atlas-iids-geo-build:
	$(PYTHON) scripts/65_build_patent_geography_from_export.py

atlas-iids-preflight:
	$(PYTHON) scripts/67_atlas_iids_preflight.py

atlas-iids-pipeline:
	$(PYTHON) scripts/64_run_atlas_iids_pipeline.py --production

atlas-iids-pipeline-full:
	$(PYTHON) scripts/64_run_atlas_iids_pipeline.py --full-chain --production

atlas-iids-smoke:
	$(PYTHON) scripts/64_run_atlas_iids_pipeline.py --detail-sql tests/fixtures/iids_base_patent_detail_sample.sql --law-status-sql tests/fixtures/iids_base_patent_law_status_sample.sql --smoke-rows 5000 --skip-geo

atlas-iids-manifest-merge:
	$(PYTHON) scripts/68_merge_patent_manifest_draft.py

atlas-iids-download-detail:
	@echo "Production machine only: requires external SSD or cloud VM with >=150 GB free."
	@echo "Set OPENXLAB_IIDS_SOURCES_DIR to external drive before running."
	$(PYTHON) scripts/59_download_iids_patent_sources.py --detail-only

atlas-iids-export-keys:
	$(PYTHON) scripts/66_export_iids_patent_keys.py --production

atlas-iids-wsl-production:
	@echo "Runs IIDS download+convert on WSL disk (~950 GB free). Requires OPENXLAB_AK/SK."
	powershell -NoProfile -File scripts/wsl_start_iids_production.ps1

atlas-iids-production-status:
	$(PYTHON) scripts/69_iids_production_status.py

atlas-iids-external-status:
	powershell -NoProfile -File scripts/windows_iids_external.ps1 -Step status

# Cloud VM production (canonical). STEP=status|docs|detail|smoke-convert|full-convert|copy-pack
atlas-iids-cloud:
	@test -n "$(STEP)" || (echo "Usage: make atlas-iids-cloud STEP=status" && exit 2)
	bash scripts/cloud_iids_production.sh $(STEP)

atlas-iids-cloud-copyback:
	bash scripts/cloud_iids_copyback.sh

atlas-iids-verify-copyback:
	$(PYTHON) scripts/70_verify_iids_copyback.py

atlas-iids-import-copyback:
	@test -n "$(ARCHIVE)" || (echo "Usage: make atlas-iids-import-copyback ARCHIVE=atlas_iids_filtered_outputs.tar.gz" && exit 2)
	bash scripts/import_iids_copyback.sh "$(ARCHIVE)"

atlas-iids-geography-brief:
	$(PYTHON) scripts/71_geography_procurement_brief.py

atlas-iids-control-post-copyback: atlas-iids-verify-copyback atlas-patent-prep atlas-iids-manifest-merge

# Control laptop: after copy-back tarball + cnipa_patent_geography_2015_2024.csv
atlas-iids-control-evidence-chain: atlas-iids-verify-copyback atlas-iids-geo-build atlas-iids-geo-validate atlas-iids-geo atlas-patent-prep atlas-iids-manifest-merge atlas-evidence-check atlas-patents atlas-v02 atlas-models-v02 atlas-status

atlas-iids-geo-fixture-smoke:
	$(PYTHON) scripts/run_iids_geo_fixture_smoke.py

atlas-v02:
	$(PYTHON) scripts/47_build_atlas_v02.py
	$(PYTHON) scripts/48_validate_atlas_v02.py

atlas-models-v02:
	$(PYTHON) scripts/49_run_atlas_models_v02.py

atlas-status:
	$(PYTHON) scripts/50_atlas_status.py --json

atlas-phase1: atlas-exposure atlas-patents atlas-smartfactories atlas-sf-audit atlas-v02 atlas-models-v02 atlas-evidence-check atlas-status

test:
	pytest -q

all: setup build baci panel analysis paper test

clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; \
	[shutil.rmtree(p, ignore_errors=True) for p in ['data/interim','data/processed','outputs']]; \
	[Path(d).mkdir(parents=True, exist_ok=True) for d in ['data/interim','data/processed','outputs/tables','outputs/figures']]"