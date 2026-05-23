from __future__ import annotations

import csv
import re
from pathlib import Path

from diffusion_state.build_paper_tables import tables_markdown_section
from diffusion_state.utils import PROJECT_ROOT

DRAFT_IN = PROJECT_ROOT / "paper" / "draft_v1.md"
DRAFT_OUT = PROJECT_ROOT / "paper" / "draft_v1_submission.md"
DRAFT_TEX = PROJECT_ROOT / "paper" / "draft_v1.tex"
CITATION_MAP = PROJECT_ROOT / "paper" / "citation_map.csv"
FIGURE_MANIFEST = PROJECT_ROOT / "paper" / "figure_manifest.json"


def _load_citation_map() -> list[dict[str, str]]:
    if not CITATION_MAP.exists():
        return []
    with CITATION_MAP.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _references_section() -> str:
    rows = _load_citation_map()
    if not rows:
        return ""
    lines = ["## References (BibTeX keys)", ""]
    lines.append("Use `paper/references.bib` with the keys below. Map draft claims via `paper/citation_map.csv`.")
    lines.append("")
    for row in rows:
        lines.append(f"- **{row['section_or_claim']}**: `@{row['bib_key']}` — {row.get('note', '')}")
    lines.append("")
    return "\n".join(lines)


def _figures_section() -> str:
    import json

    if not FIGURE_MANIFEST.exists():
        return ""
    data = json.loads(FIGURE_MANIFEST.read_text(encoding="utf-8"))
    lines = ["## Figures", ""]
    fig_num = 0
    for fig in data.get("figures", []):
        if not fig.get("main_text"):
            continue
        if fig.get("status") != "copied":
            continue
        fig_num += 1
        rel = fig["paper_path"].replace("paper/", "")
        lines.append(f"### Figure {fig_num}")
        lines.append("")
        lines.append(f"![{fig['caption']}]({rel})")
        lines.append("")
        lines.append(f"*{fig['caption']}*")
        lines.append("")
        lines.append(f"Source artifact: `{fig['source_path']}`. Claim: `{fig['claim_id']}`.")
        lines.append("")
    return "\n".join(lines)


def _strip_submission_tail(text: str) -> str:
    """Remove checklist sections replaced by export (tables, figures, owner TODOs)."""
    text = re.sub(r"\n## Tables to use in this draft\n[\s\S]*?(?=\n## )", "\n", text, count=1)
    text = re.sub(r"\n## Engineering status[\s\S]*?(?=\n## Paper owner|\Z)", "\n", text, count=1)
    text = re.sub(r"\n## Paper owner[\s\S]*?(?=\n## |\Z)", "\n", text, count=1)
    text = re.sub(r"\n## Drafting TODOs\n[\s\S]*$", "", text, count=1)
    return text.rstrip()


def export_draft_submission() -> tuple[Path, Path | None]:
    if not DRAFT_IN.exists():
        raise FileNotFoundError(f"Missing {DRAFT_IN}")

    body = _strip_submission_tail(DRAFT_IN.read_text(encoding="utf-8"))

    submission = (
        body
        + "\n\n"
        + tables_markdown_section()
        + "\n"
        + _figures_section()
        + "\n"
        + _references_section()
        + "\n## Submission package (engineering)\n\n"
        + "- Figures synced: `make paper-figures`\n"
        + "- Gates: `make pcs`\n"
        + "- Submission validation: `make validate-submission`\n"
        + "- BibTeX: `paper/references.bib`\n"
    )
    DRAFT_OUT.write_text(submission, encoding="utf-8")

    tex_path = _write_minimal_latex(submission)
    return DRAFT_OUT, tex_path


def _write_minimal_latex(markdown_body: str) -> Path | None:
    """Minimal LaTeX scaffold for journal conversion (pandoc-friendly)."""
    title_match = re.search(r"^# (.+)$", markdown_body, re.MULTILINE)
    title = title_match.group(1) if title_match else "Diffusion State Draft"
    tex = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{natbib}
\bibliographystyle{apalike}
\title{""" + title.replace("&", r"\&") + r"""}
\author{Research draft --- \texttt{paper/draft\_v1\_submission.md}}
\date{\today}
\begin{document}
\maketitle
\begin{abstract}
See markdown submission draft for full text. Build with: \texttt{make export-submission}.
\end{abstract}
\section*{Note}
This file is a conversion scaffold. Import \texttt{paper/draft\_v1\_submission.md} via Pandoc or paste section text here.
\section{Figures}
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.9\linewidth]{figures/fig_1_timing_diagnostic_pilot_zones.png}
  \caption{Timing diagnostic (not a pre-trend test).}
\end{figure}
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.9\linewidth]{figures/fig_2_city_typology_smart_factory_counts.png}
  \caption{Smart-factory projects by diffusion-state city type.}
\end{figure}
\bibliography{references}
\end{document}
"""
    DRAFT_TEX.write_text(tex, encoding="utf-8")
    return DRAFT_TEX
