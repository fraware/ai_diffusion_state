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

pip install -e .[dev]
make seed
make test
```

On Windows without GNU Make: `python scripts/00_build_seed_tables.py` then `pytest -q`.

## Pipeline commands

| Command | Purpose |
|---|---|
| `make setup` | Editable install with dev dependencies |
| `make seed` | Build verified tables (pilot zones) from `data/seed/` |
| `make fetch` | Snapshot public HTML sources (network) |
| `make build` | All analysis-ready tables available without raw downloads |
| `make parse` | Parse smart-factory HTML when `data/raw/` is populated |
| `make baci` | Build export outcomes when BACI files are in `data/raw/baci/` |
| `make panel` | Merge city-year analysis panel |
| `make analysis` | Baseline regressions and event study |
| `make test` | Schema and validation tests |

Target end state:

```bash
make fetch && make build && make test && make analysis
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
| 2 — Smart factories | Parser scaffold; needs raw MIIT lists |
| 3 — BACI exports | Module scaffold; needs HS17 download |
| 4 — City controls | Not started |
| 5 — Baseline analysis | Script stubs |
| 6 — Paper integration | Not started |

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

## License and data

Raw BACI and EPS/NBS city statistics require separate download or license. See `configs/sources.yml` and `.env.example`.
