from __future__ import annotations

import time
from pathlib import Path

import requests

from diffusion_state.utils import PROJECT_ROOT, ensure_dir, read_yaml

HEADERS = {
    "User-Agent": "Mozilla/5.0 research bot; contact: research-team@example.org"
}


def fetch_source_pages(config_path: Path | None = None) -> list[Path]:
    config_path = config_path or PROJECT_ROOT / "configs" / "sources.yml"
    sources = read_yaml(config_path)["sources"]
    out_paths: list[Path] = []

    for key, meta in sources.items():
        local_path = meta.get("local_path")
        if not local_path or not str(local_path).startswith("data/raw/"):
            continue
        if not local_path.endswith((".html", ".htm")):
            continue
        url = meta["url"]
        out = ensure_dir(PROJECT_ROOT / Path(local_path).parent) / Path(local_path).name
        if out.exists():
            out_paths.append(out)
            continue
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        out.write_text(resp.text, encoding=resp.encoding or "utf-8")
        out_paths.append(out)
        time.sleep(1.0)
    return out_paths


if __name__ == "__main__":
    paths = fetch_source_pages()
    print(f"Fetched {len(paths)} source pages")
