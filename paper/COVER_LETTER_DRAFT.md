# Cover letter draft (PCS measurement paper)

**Regenerate:** `make cover-letter` after `make pcs`.

---

Dear Editor,

We submit our manuscript on China's hub-centered industrial AI adoption architecture, linking national AI pilot zones to Ministry of Industry and Information Technology excellence-level smart-factory recognition.

**Data and measurement.** We construct a reproducible dataset of 17 AI pilot-zone units and 509 listed smart-factory projects (2024–2025), with evidence-classified city assignment (official=102, rule_based=357, external=50). A stratified audit supports the resolution protocol. This is not a claim that all assignments are externally audited.

**Empirical contribution.** The paper documents strong descriptive overlap between pilot-zone geography and listed smart-factory recognition, then shows that the association attenuates when major hubs and direct-admin municipalities are removed—consistent with a hub-centered diffusion architecture rather than a uniform treatment effect. We do not estimate a causal average treatment effect of pilot-zone designation.

**Robustness.** Appendix Table I reports partial 2024 public city controls (Table I OLS count: pilot_zone coef=1.58, p=0.020, N=51, R2=0.52 (appendix only; not EPS-equivalent)). Strict EPS/NBS controlled specifications remain unavailable by design until licensed city economic controls are ingested.

**Replication.** Engineering gates: PCS ready=True, submission package ready=True. Replication package: `paper/submission_bundle/` (or `paper/submission_bundle.zip`) with manifest `paper/SUBMISSION_MANIFEST.json`. Rebuild: `make pcs` at git commit `1eef76f-dirty` (working tree has uncommitted changes).

We believe the paper fits [JOURNAL NAME] because it offers a measurement framework for industrial AI diffusion distinct from frontier-model capability rankings.

Sincerely,

[Author names and affiliations]

Git commit: `1eef76f-dirty` (working tree has uncommitted changes)
