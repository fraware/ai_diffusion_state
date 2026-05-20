from __future__ import annotations

import ssl
import urllib.request
import zipfile
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT, ensure_dir

BACI_HS17_ZIP_URL = "https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS17_V202601.zip"
BACI_HS17_ZIP_NAME = "BACI_HS17_V202601.zip"
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def fetch_baci_hs17(
    baci_dir: Path | None = None,
    url: str = BACI_HS17_ZIP_URL,
    force: bool = False,
) -> Path:
    """Download and extract CEPII BACI HS17 (202601 release) yearly CSV files."""
    baci_dir = ensure_dir(baci_dir or PROJECT_ROOT / "data" / "raw" / "baci")
    zip_path = baci_dir / BACI_HS17_ZIP_NAME
    existing = sorted(baci_dir.glob("BACI_HS17_Y*_V*.csv"))
    if existing and not force:
        return zip_path

    if not zip_path.exists() or force:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research"})
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=600) as resp:
            zip_path.write_bytes(resp.read())

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith(".csv") and "BACI_HS17_Y" in member:
                target = baci_dir / Path(member).name
                if not target.exists() or force:
                    zf.extract(member, path=baci_dir)
                    extracted = baci_dir / member
                    if extracted != target and extracted.exists():
                        extracted.rename(target)
    return zip_path


if __name__ == "__main__":
    path = fetch_baci_hs17()
    n = len(list(path.parent.glob("BACI_HS17_Y*_V*.csv")))
    print(f"BACI HS17 ready under {path.parent} ({n} yearly CSV files)")
