# Engineer next steps (PCS / hub-diffusion paper)

**Paper frame:** China's AI diffusion state is a **hub-centered industrial adoption architecture**. Pilot zones mark part of this architecture; the evidence does **not** establish a uniform average treatment effect.

**Draft only from** `paper/main_tables/` (Tables A–G). Do not draft from Table 4/12, stub Table 5, or pending Table 17 until qualified.

---

## Step 1 — Synchronize paper-facing numbers

**Owner:** Paper owner or Engineer E.

**Commands:**

```bash
make analysis
make sync-paper-stats
make main-tables
make paper
make validate-sprint
make test
```

**Auto-synced files** (PCS markers): `paper/results_memo.md`, `paper/red_team_memo.md`, `paper/reviewer_results_snapshot.md`.

**Acceptance:** No stale values (`125 cities`, `382 projects`, `8.33 vs 2.83`, `≥250 resolved`, `audited override` in claim text). Current build targets: **160** adoption cities, **507** Table 6 full-sample projects, baseline coef **~4.55**, direct-admin **~2.90**, top-5 SF **~2.95**, pilot vs non-pilot means **12.00 vs 2.22**.

---

## Step 2 — City-resolution audit (Table 17)

**Owner:** Engineer B.

Fill `data/audit/city_resolution_sample_audit.csv`:

- `auditor_decision`: `confirmed` | `incorrect` | `uncertain` | `insufficient_evidence`
- Minimum: **50** `rule_based_text_inference` + **20** `official_location_exact` (no external rows yet)

```bash
make validate-audit    # fails until decisions filled
make recompute-audit
make sync-paper-stats
```

**Acceptance:** Paper states either completed audit rates **or** audit pending with rule-based caveats. Do not claim "externally audited city resolution" until done.

---

## Step 3 — Language: city-resolution rules (not "audited overrides")

**Owner:** Paper owner + Engineer B.

Use: **city-resolution rules**, **rule-based city assignments**, **city-resolution register**.

Avoid: **audited overrides**, **externally verified** (unless `external_evidence_url` is a non-list source).

**Required sentence:** All 509 projects are assigned to cities: **102** official-location exact, **407** rule-based, **0** externally verified until non-list URLs are added.

---

## Step 4 — External verification mini-sprint

**Owner:** Engineer B.

Target: **≥50** `external_evidence_verified` rows (high-impact: top SF cities, pilots, hub-exclusion cities, `firm_registry_match`, advanced export sectors).

Prioritized queue (auto-built): `data/interim/external_verification_queue.csv` via `make external-verification-queue`.

Per row: `external_evidence_url`, `external_evidence_type`, `resolution_class=external_evidence_verified`, `audit_notes`.

```bash
make external-verification-queue
make geo-audit
make validate-geo
make analysis
make main-tables
make paper
make test
```

---

## Step 5 — Real city controls (EPS/NBS)

**Owner:** Engineer A.

Place files in `data/raw/city_controls/` (see `data/raw/city_controls/README.md`).

```bash
make city-controls
make panel
make analysis
make main-tables
make paper
make validate-sprint
make production-check
make test
```

**Acceptance:** Table 5–8 from EPS/NBS; no stub coefficients in paper text.

---

## Step 6 — Production mode guard

**Owner:** Engineering lead.

```bash
make production-check
```

Implemented: `scripts/17_validate_production_outputs.py`. Fails on stub leakage in paper paths and stale numeric phrases.

---

## Step 7 — Ex ante typology control source

**Owner:** Engineer D.

`table_18_city_diffusion_typology_ex_ante.csv` includes `typology_control_source`:

- `real_city_controls` — may use `top_10_gdp_city`
- `stub_controls` / `no_controls` — typology uses only `pilot_zone`, `direct_admin_municipality`, `mega_hub`

---

## Step 8 — Province-year = coarse robustness

**Owner:** Engineer D + paper owner.

`claim_table_map.csv`: `province_year_robustness` → `coarse_robustness`.

Paper text: province-level results are a coarse check; pilot provinces contain non-pilot cities.

---

## Step 9 — Geo coverage language

Replaced ≥250 target with evidence-quality framing (auto-synced `PCS:GEO_COVERAGE` in results memo).

---

## Step 10 — Draft from main tables

| Table | Source |
|-------|--------|
| A | `table_A_dataset_counts.csv` |
| B | `table_B_city_resolution_quality.csv` |
| C | `table_C_pilot_overlap.csv` |
| D | `table_D_hub_exclusion.csv` |
| E | `table_E_city_typology.csv` |
| E ex ante | `table_E_ex_ante_city_typology.csv` |
| F | `table_F_ex_ante_industry_heterogeneity.csv` |
| G | `table_G_export_relevance.csv` |
| H | `table_H_export_sector_share_comparison.csv` |

---

## Assignment summary

| Engineer | Focus |
|----------|--------|
| **A** | EPS/NBS controls; controlled Models 4–7 |
| **B** | Audit decisions + ≥50 external verifications |
| **C** | Export strategic relevance (Table G); no causal export |
| **D** | Production guard, typology flags, province-year tier |
| **Paper** | Draft from main tables; hub-centered framing |
