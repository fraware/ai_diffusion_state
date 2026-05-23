from __future__ import annotations

import subprocess
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT


def get_git_revision(cwd: Path | None = None) -> dict[str, str | bool]:
    """Return git revision metadata for submission traceability."""
    cwd = cwd or PROJECT_ROOT
    try:
        full = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        short = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=cwd,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        )
        return {"full": full, "short": short, "dirty": dirty, "available": True}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"full": "", "short": "", "dirty": False, "available": False}


def format_revision_label(revision: dict[str, str | bool] | None = None) -> str:
    rev = revision or get_git_revision()
    if not rev.get("available") or not rev.get("short"):
        return "unknown (not a git checkout)"
    label = str(rev["short"])
    if rev.get("dirty"):
        label += "-dirty"
    return label
