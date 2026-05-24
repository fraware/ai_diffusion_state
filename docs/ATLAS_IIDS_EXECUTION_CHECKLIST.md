# Atlas IIDS execution checklist

Canonical path: **cloud VM** does heavy lift; **control laptop** does gates and paper.

Run `make atlas-iids-workflow` at any time for live phase status.

## Phase 0 — Repository (control laptop)

- [ ] `git pull` and confirm `git rev-parse HEAD` is current (`bf6ae19` or later)
- [ ] `make pcs-guard` passes
- [ ] `make atlas-iids-workflow` shows repo tooling complete

## Phase 1 — Cloud VM provision

- [ ] Ubuntu 22.04 or 24.04, **300 GB disk minimum** (500 GB safer)
- [ ] 8–16 vCPU, 32 GB RAM preferred
- [ ] Rotated `OPENXLAB_AK` / `OPENXLAB_SK` (not committed)
- [ ] `bash scripts/cloud_vm_bootstrap.sh` on the VM

## Phase 2 — Cloud production (tmux)

```bash
tmux new -s iids
cd ~/ai_diffusion_state && source .venv/bin/activate
export OPENXLAB_AK=... OPENXLAB_SK=...
export OPENXLAB_IIDS_SOURCES_DIR=/mnt/iids_sources

make atlas-iids-cloud STEP=status
make atlas-iids-cloud STEP=docs
make atlas-iids-cloud STEP=detail        # ~136 GB; hours
make atlas-iids-cloud STEP=smoke-convert
make atlas-iids-cloud STEP=full-convert
make atlas-iids-cloud-copyback
```

- [ ] `base_patent_detail.sql` on VM only (do not copy to laptop)
- [ ] `data/raw/patents/opendatalab_iids_industrial_ai_patents_2015_2024_part1.csv` has 500+ rows
- [ ] `atlas_iids_filtered_outputs.tar.gz` created

## Phase 3 — Copy-back (control laptop)

```powershell
git pull
powershell -File scripts/import_iids_copyback.ps1 -Archive atlas_iids_filtered_outputs.tar.gz
make atlas-iids-verify-copyback
make atlas-iids-geography-brief
```

- [ ] `table_P8c_iids_copyback_verification.json` shows `ready_for_geography_procurement=true`

## Phase 4 — Geography (critical bottleneck)

- [ ] Send `data/raw/patents/iids_filtered_patent_ids_for_geography.csv` to CNIPA/Lens vendor
- [ ] Receive targeted address export only (not full patent universe)
- [ ] Place `data/raw/patents/cnipa_patent_geography_2015_2024.csv`
- [ ] `make atlas-iids-geo-validate` passes (80%+ city fill, 50+ cities, 500+ rows)

## Phase 5 — Evidence chain (control laptop)

```powershell
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json
```

Target:

```text
fixture_patents_detected = false
real_patent_source_present = true
patent_layer_ready = true
atlas_evidence_ready = true
atlas_models_ready = true
atlas_phase1_ready = true
```

## Forbidden

- Production on Windows `C:` or WSL home
- Full IIDS download (~735 GB)
- Copy 136 GB SQL to laptop
- Weaken `atlas_evidence_ready` gates
- Procurement or empirical paper claims before gates pass
- Commit OpenXLab credentials or raw proprietary SQL
