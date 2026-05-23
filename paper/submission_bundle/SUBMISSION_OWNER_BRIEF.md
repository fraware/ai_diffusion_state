# PCS submission owner brief (one page)

**Purpose:** Upload the measurement paper without re-running the pipeline.  
**Git revision:** `49a6b6c-dirty`  
**PCS ready:** `True` | **Submission ready:** `True`

## Upload these files

1. **Manuscript source:** `paper/draft_v1_submission.md` (convert to journal template first)
2. **Replication package:** `paper/submission_bundle.zip` OR folder `paper/submission_bundle/` (46 files in manifest)
3. **Cover letter:** `paper/COVER_LETTER_DRAFT.md` (edit journal name and authors)
4. **Manifest (optional for editors):** `paper/SUBMISSION_MANIFEST.json`

## Claims the paper supports (main text)

- Hub-centered industrial AI diffusion architecture (descriptive)
- Pilot-zone overlap and city typology (associational)
- Hub-exclusion attenuation (Table D)
- Ex ante industry heterogeneity (Table F)
- Export relevance descriptives (Tables G, H)

## Claims the paper does not support

- Causal average treatment effect of pilot-zone designation
- EPS/NBS-equivalent controlled adoption (strict Table 5 blocked)
- Economy-wide productivity shock proof

## Evidence hygiene (for methods section)

- official=102, rule_based=357, external=50
- 509/509 listed smart-factory projects resolved to cities
- Table I is appendix-only partial 2024 public controls

## Before you click submit

```powershell
make pcs-guard
make validate-submission
```

Atlas true-vision work is separate: `docs/ATLAS_PHASE2_REAL_EVIDENCE_INSTRUCTIONS.md`.
