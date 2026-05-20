from __future__ import annotations

import ssl
import time
import urllib.request
from pathlib import Path

from diffusion_state.utils import PROJECT_ROOT, ensure_dir, read_yaml

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research bot"
}
_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def fetch_source_pages(config_path: Path | None = None) -> list[Path]:
    config_path = config_path or PROJECT_ROOT / "configs" / "sources.yml"
    sources = read_yaml(config_path)["sources"]
    out_paths: list[Path] = []

    for key, meta in sources.items():
        local_path = meta.get("local_path")
        if not local_path or not str(local_path).startswith("data/raw/"):
            continue
        if not str(local_path).endswith((".html", ".htm")):
            continue
        url = meta["url"]
        out = ensure_dir(PROJECT_ROOT / Path(local_path).parent) / Path(local_path).name
        if out.exists():
            out_paths.append(out)
            continue
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=_SSL_CONTEXT, timeout=90) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        out.write_text(html, encoding="utf-8")
        out_paths.append(out)
        time.sleep(1.0)
    return out_paths


if __name__ == "__main__":
    paths = fetch_source_pages()
    print(f"Fetched {len(paths)} source pages")
