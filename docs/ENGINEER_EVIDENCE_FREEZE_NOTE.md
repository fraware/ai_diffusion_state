# Engineer evidence-freeze note (required once)

Paper drafting can proceed in parallel. Send **only** the items below—no new geography work, Lens batches, or infrastructure.

---

## Template (copy, fill, email or attach)

**Repository:** `fraware/ai_diffusion_state`  
**Evidence-freeze date:** ___________

1. **Latest commit SHA:** `________________________________`
2. **`make pcs-paper-owner`:** PASS / FAIL
3. **`make validate-submission`:** PASS / FAIL
4. **`make atlas-iids-tiered-extension`:** PASS / FAIL *(or `make atlas-iids-frozen-verify` if extension was not rerun)*
5. **`make atlas-paper-claim-guard`:** PASS / FAIL
6. **Attach:** `paper/atlas_gate_report.json`
7. **`paper/main_tables/` file list:** *(paste `dir` / `ls` output)*
8. **Attach:** `outputs/tables/table_P14_tiered_geography_coverage_by_confidence.csv`
9. **Attach:** `outputs/tables/table_P17_tiered_geography_tier_breakdown.csv`
10. **Attach:** `outputs/tables/table_P17_tiered_robustness_audit.csv`
11. **`ready_for_evidence_chain`:** remains **false** — CONFIRMED
12. **`exact_geography_ready`:** remains **false** — CONFIRMED
13. **`ready_for_tiered_robustness_patent_layer`:** **true** — CONFIRMED
14. **Table I (`table_I_appendix_public_fallback_controls`):** appendix-only — CONFIRMED
15. **Strict EPS/NBS Table 5:** blocked — CONFIRMED

Optional (do not block drafting): `paper/FINAL_ARTIFACT_INVENTORY.md` if missing.

---

## What engineers must stop doing

Stop all routine work on:

- manual applicant mapping
- Lens exports
- new geography inference rules
- Hetzner / OpenXLab reruns
- deprecated phase Makefile targets (`atlas-iids-tiered-geography`, manual phase c/d/f/g)
- new patent claims or publication F1 language
- new infrastructure

The tiered geography robustness layer is **frozen** at ~65.36% city fill. It is a **robustness baseline** only. Exact geography and the 80% publication gate remain **blocked**.

---

## Commands to run before sending

```powershell
git pull origin main
make pcs-paper-owner
make validate-submission
make atlas-iids-tiered-extension
make atlas-paper-claim-guard
```

Fast tiered diagnostics only (if extension already built):

```powershell
make atlas-iids-frozen-verify
```
