# The Diffusion State

**China's AI Industrialization Model and the Next Productivity Shock**

Empirical pipeline for an NBER Economics of AI (China) brief measuring whether China's AI diffusion system—pilot zones, smart-factory adoption, industrial AI projects, and export upgrading—forms a coherent institutional chain.

## Core empirical chain

```text
AI pilot zones → smart-factory adoption → industrial AI diffusion → export & productivity upgrading
```

## Repository layout

```text
configs/           source registry, keywords, city aliases
data/
  seed/            manually verified small tables (committed)
  raw/             downloaded sources (gitignored)
  interim/         parsed tables (gitignored)
  processed/       analysis-ready tables (gitignored, built by scripts)
docs/
  DATA_CONTRACTS.md
  source_notes/
scripts/           numbered pipeline entry points
src/diffusion_state/
tests/
outputs/
  tables/
  figures/
```

## Quickstart

```bash
git clone https://github.com/fraware/ai_diffusion_state.git
cd ai_diffusion_state
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

make setup
make seed
make test
```

`make setup` installs the package and dependencies (including `beautifulsoup4` for HTML parsing). Run it once per environment before `make build` or `make test`.

On Windows without GNU Make: `pip install -e .[dev]` then `python scripts/00_build_seed_tables.py` and `pytest -q`.

Git Bash path note: use `cd ~/ai_diffusion_state` or `cd /c/Users/mateo/ai_diffusion_state`, not `cd c:\Users\...` (backslashes are stripped).

## Pipeline commands

| Command | Purpose |
|---|---|
| `make setup` | Editable install with dev dependencies |
| `make seed` | Build verified tables (pilot zones) from `data/seed/` |
| `make fetch` | Snapshot public HTML sources (network) |
| `make build` | All analysis-ready tables available without raw downloads |
| `make parse` | Parse smart-factory HTML when `data/raw/` is populated |
| `make baci` | Download CEPII BACI HS17 (if needed) and build export outcomes |
| `make panel` | Merge city-year analysis panel |
| `make analysis` | Baseline regressions and event study |
| `make test` | Schema and validation tests |

Target end state:

```bash
    make fetch && make build && make test && make analysis && make paper
```

## Data governance

1. Never edit files under `data/raw/`.
2. Do not commit large proprietary downloads.
3. Every processed row must trace to a `source_url` or raw file.
4. Inferred fields require confidence flags (smart-factory pipeline).
5. Manual fixes go in seed or correction tables, not generated CSVs.
6. Scripts must be idempotent; paper tables come from scripts, not notebooks.

## Current status

| Phase | Status |
|---|---|
| 0 — Repo activation | CI, tests, gitignore, Makefile |
| 1 — Pilot zones | 17-zone seed → `pilot_zones.csv` with canonical schema |
| 2 — Smart factories | 2024/2025 parsed (235+274); clean + city panels; city geo memo |
| 3 — BACI exports | HS17 2017–2024 built from CEPII 202601 (`make baci`) |
| 4 — City controls | Ingestion module ready; requires EPS/NBS export in `data/raw/city_controls/` |
| 5 — Baseline analysis | Overlap tables, adoption models, event-study figure, memo v1 |
| 6 — Paper integration | Outline, appendices, red-team memo, `make paper` manifest |

## Priority order (if time is scarce)

1. Pilot zones
2. 2024 smart-factory list
3. City-year adoption table
4. Descriptive pilot-zone overlap
5. BACI export outcomes
6. City controls
7. Event study

## Documentation

- [Research design](docs/research_design.md)
- [Data dictionary](docs/data_dictionary.md) (legacy columns; see [DATA_CONTRACTS](docs/DATA_CONTRACTS.md))
- [Pilot zone source notes](docs/source_notes/pilot_zones.md)
- [Engineering brief](docs/engineering_brief.md)
- [Reproducibility](docs/REPRODUCIBILITY.md)
- [Paper outline](paper/outline.md)
- [Paper results memo](paper/results_memo.md)
- [Red-team memo](paper/red_team_memo.md)

## License and data

Raw BACI and EPS/NBS city statistics require separate download or license. See `configs/sources.yml` and `.env.example`.

## Atlas IIDS patent evidence (active sprint)

Software is ready; **evidence is not** until real IIDS + geography exports are ingested on a **cloud VM** (not the control laptop `C:` drive).

| Command | Where |
|---------|--------|
| `make atlas-iids-workflow` | Control laptop — phase dashboard |
| `make atlas-iids-preflight` | Control laptop — disk/credential checks |
| `bash scripts/cloud_vm_bootstrap.sh` | Fresh Ubuntu VM — one-shot setup |
| `make atlas-iids-cloud STEP=...` | Cloud VM — download + convert |
| `make atlas-iids-import-copyback ARCHIVE=...` | Control laptop — after `scp` |
| `make atlas-iids-control-evidence-chain` | Control laptop — after geography file |

Playbooks:

- [IIDS clean-restart runbook](docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md)
- [IIDS execution checklist](docs/ATLAS_IIDS_EXECUTION_CHECKLIST.md)
- [Patent raw data README](data/raw/patents/README.md)
