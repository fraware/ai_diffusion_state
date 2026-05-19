from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def read_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def normalize_cn_text(x: str | None) -> str:
    if x is None:
        return ""
    x = str(x)
    x = re.sub(r"\s+", "", x)
    return x.strip()


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    text = normalize_cn_text(text)
    return any(k in text for k in keywords)


def write_csv(df: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
