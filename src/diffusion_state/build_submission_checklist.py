from __future__ import annotations

import json
from pathlib import Path

from diffusion_state.pcs_status import collect_pcs_gates, pcs_ready
from diffusion_state.utils import PROJECT_ROOT

CHECKLIST_PATH = PROJECT_ROOT / "paper" / "SUBMISSION_CHECKLIST.md"


def build_submission_checklist() -> str:
    gates = collect_pcs_gates()
    report_path = PROJECT_ROOT / "paper" / "pcs_gate_report.json"
    submission_ready = False
    if report_path.exists():
        submission_ready = bool(json.loads(report_path.read_text(encoding="utf-8")).get("submission_ready"))

    lines = [
        "# PCS submission checklist (auto-generated)",
        "",
        f"**PCS gates ready:** `{pcs_ready(gates)}`",
        f"**Submission package ready:** `{submission_ready}`",
        "",
        "Regenerate: `make submission-checklist` after `make pcs`.",
        "",
        "## Engineering gates",
        "",
    ]
    for g in gates:
        mark = "x" if g.passed else " "
        lines.append(f"- [{mark}] **{g.name}** — {g.detail}")
    lines.extend(
        [
            "",
            "## Paper owner (manual)",
            "",
            "- [ ] Journal template applied (`paper/draft_v1_submission.md` → Word/LaTeX)",
            "- [ ] Author affiliations and acknowledgments",
            "- [ ] Table/figure numbering matches journal style",
            "- [ ] Cover letter cites git commit and `paper/SUBMISSION_MANIFEST.json`",
            "- [ ] Table I labeled appendix-only in submitted PDF",
            "- [ ] No strict Table 5 in main text unless EPS/NBS ingested",
            "",
            "## Rebuild",
            "",
            "```powershell",
            "make pcs",
            "make validate-submission",
            "```",
            "",
        ]
    )
    text = "\n".join(lines)
    CHECKLIST_PATH.write_text(text, encoding="utf-8")
    return text
