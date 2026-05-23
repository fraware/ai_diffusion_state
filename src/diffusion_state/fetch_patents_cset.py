from __future__ import annotations

import ssl
import urllib.request
import zipfile
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT, ensure_dir

CSET_ZIP_URL = (
    "https://raw.githubusercontent.com/georgetown-cset/1790-ai-patent-data/master/patent_database.csv.zip"
)
CSET_ZIP_NAME = "cset_patent_database.csv.zip"
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def fetch_cset_patent_database(
    patents_dir: Path | None = None,
    force: bool = False,
) -> Path:
    """Download CSET 1790 AI patent index (~5 MB zip) for taxonomy validation."""
    patents_dir = ensure_dir(patents_dir or PROJECT_ROOT / "data" / "raw" / "patents")
    zip_path = patents_dir / CSET_ZIP_NAME
    csv_path = patents_dir / "patent_database.csv"

    if csv_path.exists() and not force:
        return csv_path

    if not zip_path.exists() or force:
        req = urllib.request.Request(CSET_ZIP_URL, headers={"User-Agent": "Mozilla/5.0 research"})
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=300) as resp:
            zip_path.write_bytes(resp.read())

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("patent_database.csv"):
                zf.extract(member, path=patents_dir)
                extracted = patents_dir / member
                if extracted.name != "patent_database.csv" and extracted.exists():
                    extracted.rename(csv_path)
    return csv_path
