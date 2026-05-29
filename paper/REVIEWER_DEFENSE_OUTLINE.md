# Reviewer defense outline (drafting scaffold)

Use with `paper/red_team_memo.md` and `paper/reviewer_results_snapshot.md`. Cite only artifacts in `paper/claim_table_map.csv` and `paper/FINAL_ARTIFACT_INVENTORY.md`.

---

## 1. Pilot zones are endogenous

**Objection:** Designated cities are not randomly assigned; overlap with hubs confounds “treatment.”

**Response:**

- We do **not** claim a causal average treatment effect of designation.
- Baseline association (Table C / city-year models) is **descriptive**.
- Hub-exclusion (Table D) shows attenuation when Beijing, Shanghai, Shenzhen, Hangzhou, direct-admin cities, or top-five SF cities are dropped — supports **hub-centered diffusion architecture**, not a flat pilot shock.
- Timing figure (Fig 1) is diagnostic, not a pre-trend test.

---

## 2. Smart-factory lists are administrative recognition

**Objection:** MIIT lists measure official recognition, not true adoption depth.

**Response:**

- Outcome is **listed excellence-level recognition** (509 projects, 2024–2025 lists), stated explicitly.
- Not all smart-factory activity in China — measurement boundary is the public register.
- Concentration in pilot and high-capacity cities is a **descriptive fact** about the recognition map.

---

## 3. City assignment has uncertainty

**Objection:** Not all 509 city links are externally verified.

**Response:**

- Three evidence classes (Table 16 / main Table B): 102 official-location exact, 357 rule-based, 50 external-evidence verified.
- Stratified audit (Table 17): 70/70 decisions; official sample 20/20 confirmed; rule-based sample mixed.
- Do **not** claim full external audit of all rows — class-specific language only.

---

## 4. Public controls are partial

**Objection:** Appendix controls are not EPS-equivalent prefecture panels.

**Response:**

- Table I is **partial** 2024 ChinaUTC cross-section — labeled appendix-only in claim map.
- Strict EPS/NBS Table 5 remains **blocked** — not claimed as passed.
- OLS/log models may show positive pilot association; Poisson not significant — report both.

---

## 5. Patent geography is tiered (65.4%), not exact

**Objection:** Patent layer looks like full geocoding.

**Response:**

- Separate **tiered robustness extension** (P14/P17); **not** main identification.
- 65.4% city fill on 4,014,104 IIDS keys; tiers: HQ page, university, name-token, **34.6% unresolved**.
- **Not** exact publication-number address geocoding; `ready_for_evidence_chain: false`.
- No publication-ready F1 or pilot × patent causal claims in guarded drafts.

---

## 6. Export relevance is descriptive

**Objection:** Export tables do not prove causal upgrading.

**Response:**

- Tables G/H are **validated descriptive** — sector export baskets vs listed SF sectors.
- Mechanism section is suggestive where labeled (Table F ex ante heterogeneity).
- Claim tier in `claim_table_map.csv` governs each sentence.

---

## Suggested appendix section order

1. Table I (public controls)
2. Table 16 / 17 (geo evidence + audit)
3. Fig A1 (balance)
4. P14 / P17 (tiered patent geography — robustness only)
5. Limits paragraph (blocked items from inventory)
