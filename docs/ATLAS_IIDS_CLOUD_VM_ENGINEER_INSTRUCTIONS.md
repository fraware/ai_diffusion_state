# Atlas IIDS — cloud VM engineer instructions

**Decision:** Proceed with cloud VM production now. No further repo architecture is required unless a production run reveals a concrete failure.

**Do not** run production on the control laptop (`C:`, ~30 GB free), WSL home, or without an external SSD. The cloud VM does OpenXLab detail-only download, conversion, manifest prep, and tarball copy-back.

Confirm repo: `git rev-parse HEAD` must be **`566c78c` or later**.

**Google Cloud:** see [ATLAS_IIDS_GCP_VM_SETUP.md](ATLAS_IIDS_GCP_VM_SETUP.md) (attach 500 GB disk; do not use a 10 GB boot disk for SQL).

---

## 1. Provision the cloud VM (today)

| Spec | Value |
|------|--------|
| OS | Ubuntu 22.04 or 24.04 |
| Disk | **500 GB preferred** (300 GB minimum; use 500 GB to avoid a failed rerun) |
| CPU | 8–16 vCPU |
| RAM | 32 GB preferred |

---

## 2. Bootstrap and credentials (VM only)

```bash
git clone https://github.com/fraware/ai_diffusion_state.git
cd ai_diffusion_state
git pull
git rev-parse HEAD   # >= 566c78c

bash scripts/cloud_vm_bootstrap.sh
```

Set **rotated** OpenXLab keys on the VM only (never commit, never paste into laptop `.env` for production download):

```bash
export OPENXLAB_AK="YOUR_ROTATED_KEY"
export OPENXLAB_SK="YOUR_ROTATED_SECRET"
export OPENXLAB_IIDS_SOURCES_DIR="/mnt/iids_sources"
export OPENXLAB_INSECURE_SSL=1
export PYTHONUTF8=1
```

---

## 3. Production sequence (tmux)

```bash
cd ~/ai_diffusion_state
source .venv/bin/activate

tmux new -s iids

make atlas-iids-cloud STEP=status
make atlas-iids-cloud STEP=docs
make atlas-iids-cloud STEP=detail          # ~136 GB; many hours
make atlas-iids-cloud STEP=smoke-convert
make atlas-iids-cloud STEP=full-convert
make atlas-iids-cloud-copyback
```

Monitor or resume:

```bash
make atlas-iids-cloud STEP=status
make atlas-iids-cloud STEP=resume
```

**Download only** `base_patent_detail.sql` (detail-only). Do not download full IIDS (~735 GB).

---

## 4. Copy back (small artifacts only)

On the VM, confirm:

- `atlas_iids_filtered_outputs.tar.gz` and `.sha256` exist
- Production CSV has **500+** rows

Copy tarball to control laptop (`scp`, console download, or object storage).

**Do not copy:**

- `base_patent_detail.sql`
- OpenXLab `.cache`
- `/mnt/iids_sources` (136 GB SQL tree)

---

## 5. Control laptop — import and geography brief

```powershell
cd c:\Users\mateo\ai_diffusion_state
git pull

powershell -File scripts\import_iids_copyback.ps1 -Archive "PATH_TO\atlas_iids_filtered_outputs.tar.gz"
# Alias: -TarballPath "PATH_TO\atlas_iids_filtered_outputs.tar.gz"

make atlas-iids-verify-copyback
make atlas-iids-geography-brief
```

Send `data/raw/patents/iids_filtered_patent_ids_for_geography.csv` (and/or `outputs/tables/table_P9_iids_patent_keys_for_geography.csv`) to CNIPA/Lens/CNKI/CSMAR for **address metadata only** for those patent IDs.

Target supplement:

```text
data/raw/patents/cnipa_patent_geography_2015_2024.csv
```

Minimum acceptance (repo enforces):

- City fill rate >= 80%
- >= 50 unique cities
- >= 500 rows after join with industrial-AI filter

IIDS alone cannot satisfy city-industry-year evidence; geography is the structural bottleneck after copy-back.

---

## 6. Evidence chain (laptop, after geography file exists)

```powershell
make atlas-iids-control-evidence-chain
python scripts/50_atlas_status.py --json
```

Success:

```text
atlas_evidence_ready = true
atlas_phase1_ready = true
patent_layer_ready = true
atlas_models_ready = true
fixture_patents_detected = false
real_patent_source_present = true
```

Only then may `paper/draft_atlas_v1.md` use empirical patent claims.

---

## Forbidden

- Production on laptop `C:` or WSL home
- Full IIDS download
- Copy 136 GB SQL to laptop
- Start procurement before evidence gates pass
- Empirical paper claims before gates pass
- Treat fixture F1 as evidence
- Weaken `atlas_evidence_ready`
- New repo features unless production fails with a reproducible error

---

## References

- [Execution checklist](ATLAS_IIDS_EXECUTION_CHECKLIST.md)
- [Clean-restart runbook](ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md)
- `make atlas-iids-workflow` — live phase status on any machine
