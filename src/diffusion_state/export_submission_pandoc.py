from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT

DRAFT_MD = PROJECT_ROOT / "paper" / "draft_v1_submission.md"
OUT_DOCX = PROJECT_ROOT / "paper" / "draft_v1_submission.docx"
OUT_PDF = PROJECT_ROOT / "paper" / "draft_v1_submission.pdf"


def export_submission_pandoc() -> dict[str, str | None]:
    """Export Word/PDF via Pandoc when installed; otherwise skip gracefully."""
    result: dict[str, str | None] = {"docx": None, "pdf": None, "status": "skipped"}
    if not DRAFT_MD.exists():
        result["status"] = "missing_draft"
        return result
    if not shutil.which("pandoc"):
        result["status"] = "pandoc_not_installed"
        return result

    bib = PROJECT_ROOT / "paper" / "references.bib"
    resource_path = PROJECT_ROOT / "paper"

    cmd_docx = [
        "pandoc",
        str(DRAFT_MD),
        "-o",
        str(OUT_DOCX),
        "--resource-path",
        str(resource_path),
        "--from",
        "markdown",
        "--to",
        "docx",
    ]
    if bib.exists():
        cmd_docx.extend(["--citeproc", f"--bibliography={bib}"])

    subprocess.run(cmd_docx, check=True, cwd=PROJECT_ROOT)
    result["docx"] = str(OUT_DOCX.relative_to(PROJECT_ROOT))

    if shutil.which("pdflatex"):
        cmd_pdf = [
            "pandoc",
            str(DRAFT_MD),
            "-o",
            str(OUT_PDF),
            "--resource-path",
            str(resource_path),
            "--from",
            "markdown",
            "--pdf-engine",
            "pdflatex",
        ]
        if bib.exists():
            cmd_pdf.extend(["--citeproc", f"--bibliography={bib}"])
        try:
            subprocess.run(cmd_pdf, check=True, cwd=PROJECT_ROOT)
            result["pdf"] = str(OUT_PDF.relative_to(PROJECT_ROOT))
        except subprocess.CalledProcessError:
            result["pdf"] = None
    result["status"] = "ok"
    return result
