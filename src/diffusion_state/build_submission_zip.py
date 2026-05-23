from __future__ import annotations

import zipfile
from pathlib import Path

from diffusion_state.build_submission_bundle import BUNDLE_DIR
from diffusion_state.utils import PROJECT_ROOT

ZIP_PATH = PROJECT_ROOT / "paper" / "submission_bundle.zip"


def build_submission_zip() -> Path:
    if not BUNDLE_DIR.exists():
        raise FileNotFoundError("missing paper/submission_bundle/ — run make submission-bundle first")
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fp in sorted(BUNDLE_DIR.rglob("*")):
            if fp.is_file():
                arcname = fp.relative_to(BUNDLE_DIR).as_posix()
                zf.write(fp, arcname)
    return ZIP_PATH
