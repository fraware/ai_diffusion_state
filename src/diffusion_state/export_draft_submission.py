from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from diffusion_state.build_paper_tables import tables_markdown_section
from diffusion_state.utils import PROJECT_ROOT

DRAFT_IN = PROJECT_ROOT / "paper" / "draft_v1.md"
DRAFT_APPENDIX = PROJECT_ROOT / "paper" / "draft_v1_appendix.md"
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
    lines.append(
        "Use `paper/references.bib` with the keys below. Map draft claims via `paper/citation_map.csv`."
    )
    lines.append("")
    for row in rows:
        lines.append(f"- **{row['section_or_claim']}**: `@{row['bib_key']}` — {row.get('note', '')}")
    lines.append("")
    return "\n".join(lines)


def _figures_section(*, main_text_only: bool) -> str:
    if not FIGURE_MANIFEST.exists():
        return ""
    data = json.loads(FIGURE_MANIFEST.read_text(encoding="utf-8"))
    heading = "## Figures" if main_text_only else "## Appendix figures"
    lines = [heading, ""]
    fig_num = 0
    for fig in data.get("figures", []):
        if fig.get("main_text") != main_text_only:
            continue
        if fig.get("status") != "copied":
            continue
        fig_num += 1
        rel = fig["paper_path"].replace("paper/", "")
        label = "Figure" if main_text_only else "Appendix figure"
        lines.append(f"### {label} {fig_num}")
        lines.append("")
        lines.append(f"![{fig['caption']}]({rel})")
        lines.append("")
        lines.append(f"*{fig['caption']}*")
        lines.append("")
        lines.append(f"Source: `{fig['source_path']}`. Claim: `{fig['claim_id']}`.")
        lines.append("")
    return "\n".join(lines) if fig_num else ""


def _appendix_section() -> str:
    if not DRAFT_APPENDIX.exists():
        return ""
    body = DRAFT_APPENDIX.read_text(encoding="utf-8")
    # Drop duplicate top-level title for embedding
    body = re.sub(r"^# Appendix[^\n]*\n+", "", body, count=1)
    return "\n\n---\n\n# Appendix material\n\n" + body.strip() + "\n"


def _strip_submission_tail(text: str) -> str:
    """Remove checklist sections replaced by export (tables, figures, owner TODOs)."""
    for heading in (
        r"## Figures\n[\s\S]*?(?=\n## )",
        r"## Tables to use in this draft\n[\s\S]*?(?=\n## )",
        r"## Engineering status[\s\S]*?(?=\n## Paper owner|\Z)",
        r"## Paper owner[\s\S]*?(?=\n## |\Z)",
        r"## Drafting TODOs\n[\s\S]*$",
    ):
        text = re.sub(rf"\n{heading}", "\n", text, count=1)
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
        + _figures_section(main_text_only=True)
        + "\n"
        + _appendix_section()
        + "\n"
        + _figures_section(main_text_only=False)
        + "\n"
        + _references_section()
        + "\n## Submission package (engineering)\n\n"
        + "- Regenerate: `make paper-draft-export`\n"
        + "- Gates: `make validate-submission`\n"
        + "- BibTeX: `paper/references.bib`\n"
    )
    DRAFT_OUT.write_text(submission, encoding="utf-8")

    tex_path = _write_minimal_latex()
    return DRAFT_OUT, tex_path


def _write_minimal_latex() -> Path | None:
    """LaTeX scaffold with current main-text figures from manifest."""
    title = "The Diffusion State"
    if DRAFT_IN.exists():
        m = re.search(r"^# (.+)$", DRAFT_IN.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            title = m.group(1)

    fig_blocks: list[str] = []
    if FIGURE_MANIFEST.exists():
        data = json.loads(FIGURE_MANIFEST.read_text(encoding="utf-8"))
        n = 0
        for fig in data.get("figures", []):
            if not fig.get("main_text") or fig.get("status") != "copied":
                continue
            n += 1
            rel = fig["paper_path"].replace("paper/", "")
            cap = fig.get("caption", "").replace("_", r"\_")
            fig_blocks.append(
                f"\\begin{{figure}}[ht]\n"
                f"  \\centering\n"
                f"  \\includegraphics[width=0.92\\linewidth]{{{rel}}}\n"
                f"  \\caption{{{cap}}}\n"
                f"\\end{{figure}}"
            )

    figures_tex = "\n".join(fig_blocks) if fig_blocks else "% Run make paper-figures"

    tex = rf"""\documentclass[11pt]{{article}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{hyperref}}
\usepackage{{natbib}}
\bibliographystyle{{apalike}}
\title{{{title.replace("&", r"\&")}}}
\author{{Research draft --- \texttt{{paper/draft\_v1\_submission.md}}}}
\date{{\today}}
\begin{{document}}
\maketitle
\begin{{abstract}}
See \texttt{{paper/draft\_v1\_submission.md}} for full text (Pass 1--6 + appendix).
\end{{abstract}}
\section*{{Note}}
Import \texttt{{paper/draft\_v1\_submission.md}} via Pandoc or paste section text here.
{figures_tex}
\bibliography{{references}}
\end{{document}}
"""
    DRAFT_TEX.write_text(tex, encoding="utf-8")
    return DRAFT_TEX
