"""Track in-flight IIDS SQL download and production progress (cloud VM or external SSD)."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from diffusion_state.iids_paths import (
    DEFAULT_IIDS_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
    MIN_SQL_DOWNLOAD_GB,
    resolve_iids_sources_dir,
)
from diffusion_state.iids_patent_converter import find_iids_sql_paths
from diffusion_state.utils import PROJECT_ROOT

CLOUD_LOG = PROJECT_ROOT / "outputs" / "logs" / "iids_cloud_production.log"
WSL_LOG = PROJECT_ROOT / "outputs" / "logs" / "iids_wsl_production.log"
STATUS_JSON = PROJECT_ROOT / "outputs" / "tables" / "table_P8b_iids_production_status.json"
IIDS_SQL_TARGET_GB = 135.83
_PROGRESS_RE = re.compile(
    r"File Progress:\s*([0-9.]+)\s*%.*?Speed:\s*([^|]+)\|.*?ETA:\s*([0-9.]+)s"
)


@dataclass(frozen=True)
class ProductionStatus:
    phase: str
    production_host: str
    sources_dir: str
    sql_detail_present: bool
    sql_detail_size_gb: float
    sql_download_pct: float | None
    download_speed: str
    eta_seconds: float | None
    iids_output_rows: int
    log_path: str
    log_updated_seconds_ago: float | None
    production_active: bool
    sources_bytes: int | None
    disk_free_gb_sources: float | None
    recommended_next: str

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "production_host": self.production_host,
            "sources_dir": self.sources_dir,
            "sql_detail_present": self.sql_detail_present,
            "sql_detail_size_gb": round(self.sql_detail_size_gb, 3),
            "sql_download_pct": self.sql_download_pct,
            "download_speed": self.download_speed,
            "eta_seconds": self.eta_seconds,
            "eta_hours": round(self.eta_seconds / 3600, 1) if self.eta_seconds else None,
            "iids_output_csv": str(DEFAULT_IIDS_OUTPUT),
            "iids_output_rows": self.iids_output_rows,
            "keys_alias_csv": str(FILTERED_PATENT_IDS_FOR_GEO_OUTPUT),
            "log_path": self.log_path,
            "log_updated_seconds_ago": self.log_updated_seconds_ago,
            "production_active": self.production_active,
            "sources_bytes": self.sources_bytes,
            "disk_free_gb_sources": self.disk_free_gb_sources,
            "recommended_next": self.recommended_next,
        }


def _file_rows(path: Path) -> int:
    if not path.exists():
        return 0
    import csv

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def _parse_log_progress(log_text: str) -> tuple[float | None, str, float | None]:
    matches = _PROGRESS_RE.findall(log_text)
    if not matches:
        return None, "", None
    pct_s, speed, eta_s = matches[-1]
    try:
        return float(pct_s), speed.strip(), float(eta_s)
    except ValueError:
        return None, speed.strip(), None


def _dir_size_bytes(path: Path) -> int | None:
    if not path.exists():
        return None
    total = 0
    try:
        for child in path.rglob("*"):
            if child.is_file():
                total += child.stat().st_size
    except OSError:
        return None
    return total


def _disk_free_gb(path: Path) -> float | None:
    try:
        return shutil.disk_usage(path if path.exists() else path.parent).free / (1024**3)
    except OSError:
        return None


def _wsl_sources_bytes() -> int | None:
    try:
        proc = subprocess.run(
            ["wsl.exe", "-d", "Ubuntu", "bash", "-lc", "du -sb ~/iids_sources 2>/dev/null | cut -f1"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None
        return int(proc.stdout.strip().split()[0])
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def _log_age_seconds(path: Path) -> float | None:
    if not path.exists():
        return None
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return (datetime.now(tz=UTC) - mtime).total_seconds()


def _resolve_log_path() -> Path:
    if CLOUD_LOG.exists():
        return CLOUD_LOG
    if WSL_LOG.exists():
        return WSL_LOG
    return CLOUD_LOG


def _infer_production_host(sources_dir: Path) -> str:
    norm = sources_dir.as_posix().lower()
    if norm.startswith("/mnt/iids") or norm.startswith("/home/") and "iids" in norm:
        return "cloud_vm"
    if sources_dir.drive and sources_dir.drive.upper() in {"D:", "E:", "F:"}:
        return "external_ssd"
    if "/home/" in norm:
        return "wsl_home_forbidden"
    return "control_laptop"


def collect_production_status(*, sources_dir: Path | None = None) -> ProductionStatus:
    sources_dir = (sources_dir or resolve_iids_sources_dir()).resolve()
    host = _infer_production_host(sources_dir)

    detail, _ = find_iids_sql_paths(sources_dir)
    sql_gb = detail.stat().st_size / (1024**3) if detail and detail.exists() else 0.0
    output_rows = _file_rows(DEFAULT_IIDS_OUTPUT)
    sources_bytes = _dir_size_bytes(sources_dir) or _wsl_sources_bytes()
    disk_free = _disk_free_gb(sources_dir)

    log_path = _resolve_log_path()
    log_age = _log_age_seconds(log_path)
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    pct, speed, eta = _parse_log_progress(log_text)
    active = bool(log_age is not None and log_age < 300 and "full-convert complete" not in log_text.lower())

    if output_rows >= 500:
        phase = "convert_complete"
        nxt = "bash scripts/cloud_iids_copyback.sh (VM) then make atlas-iids-control-evidence-chain (laptop)"
    elif sql_gb >= IIDS_SQL_TARGET_GB * 0.99:
        phase = "convert_pending"
        nxt = "bash scripts/cloud_iids_production.sh smoke-convert && full-convert"
    elif detail and detail.exists() and sql_gb > 1:
        phase = "convert_pending"
        nxt = "bash scripts/cloud_iids_production.sh full-convert"
    elif active or (pct is not None and pct < 99.9):
        phase = "sql_download"
        nxt = "bash scripts/cloud_iids_production.sh detail  # monitor in tmux"
    elif host == "control_laptop" and (disk_free or 0) < MIN_SQL_DOWNLOAD_GB:
        phase = "blocked_control_laptop"
        nxt = "Provision cloud VM (300 GB+). bash scripts/cloud_iids_production.sh docs"
    elif "full-convert complete" in log_text.lower():
        phase = "convert_complete"
        nxt = "bash scripts/cloud_iids_copyback.sh"
    else:
        phase = "not_started"
        nxt = "bash scripts/cloud_iids_production.sh status && docs && detail"

    if pct is None and sources_bytes:
        pct = min(100.0, (sources_bytes / (IIDS_SQL_TARGET_GB * 1024**3)) * 100)

    return ProductionStatus(
        phase=phase,
        production_host=host,
        sources_dir=str(sources_dir),
        sql_detail_present=bool(detail and detail.exists() and sql_gb > 0.5),
        sql_detail_size_gb=sql_gb if sql_gb else (sources_bytes or 0) / (1024**3),
        sql_download_pct=round(pct, 2) if pct is not None else None,
        download_speed=speed,
        eta_seconds=eta,
        iids_output_rows=output_rows,
        log_path=str(log_path.relative_to(PROJECT_ROOT)),
        log_updated_seconds_ago=round(log_age, 1) if log_age is not None else None,
        production_active=active,
        sources_bytes=sources_bytes,
        disk_free_gb_sources=round(disk_free, 1) if disk_free is not None else None,
        recommended_next=nxt,
    )


def write_production_status(*, sources_dir: Path | None = None) -> dict:
    status = collect_production_status(sources_dir=sources_dir)
    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        **status.to_dict(),
    }
    STATUS_JSON.write_text(
        __import__("json").dumps(payload, indent=2),
        encoding="utf-8",
    )
    return payload
