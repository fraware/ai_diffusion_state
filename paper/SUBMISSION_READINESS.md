# Submission readiness (PCS measurement paper)

**Build date:** Regenerate with `make pcs`.  
**Gate report:** `paper/pcs_gate_report.json` must show `"ready": true`.

## Engineering complete

| Item | Status |
|------|--------|
| 509/509 city resolution | Done |
| 50 external-evidence verified | Done |
| 70/70 stratified audit | Done |
| Tables A–I in `paper/main_tables/` | Done |
| Hub-exclusion + typology + ex ante exposure | Done |
| Appendix Table I (partial 2024 controls) | Done |
| Strict Table 5 (EPS/NBS) | Blocked by design |
| `draft_v1.md` number cross-check | `make validate-draft` |
| CI PCS gate chain | `.github/workflows/ci.yml` |

## Paper owner checklist

- [ ] All statistics traced to `paper/main_tables/` (not `outputs/tables/` directly)
- [ ] Claim tiers respected (`paper/claim_table_map.csv`)
- [ ] No causal pilot-zone or export-effect language
- [ ] Table I labeled appendix / not EPS-equivalent
- [ ] Geo language: 102 official, 357 rule-based, 50 external (not "fully audited")
- [ ] Citations added to policy and data sources
- [ ] LaTeX/Word conversion and figure placement

## Forbidden main-text claims

See `docs/model_interpretation_matrix.md` and `paper/red_team_memo.md` §11.

## Rebuild before submission

```powershell
make pcs
python scripts/15_pcs_status.py --json
```
