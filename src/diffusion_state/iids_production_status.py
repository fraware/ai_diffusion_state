"""Track in-flight IIDS SQL download and WSL production progress."""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from diffusion_state.iids_paths import DEFAULT_IIDS_OUTPUT, MIN_SQL_DOWNLOAD_GB
from diffusion_state.iids_patent_converter import find_iids_sql_paths
from diffusion_state.utils import PROJECT_ROOT

PRODUCTION_LOG = PROJECT_ROOT / "outputs" / "logs" / "iids_wsl_production.log"
STATUS_JSON = PROJECT_ROOT / "outputs" / "tables" / "table_P8b_iids_production_status.json"
IIDS_SQL_TARGET_GB = 135.83
_PROGRESS_RE = re.compile(
    r"File Progress:\s*([0-9.]+)\s*%.*?Speed:\s*([^|]+)\|.*?ETA:\s*([0-9.]+)s"
)


@dataclass(frozen=True)
class ProductionStatus:
    phase: str
    sql_detail_present: bool
    sql_detail_size_gb: float
    sql_download_pct: float | None
    download_speed: str
    eta_seconds: float | None
    iids_output_rows: int
    log_path: str
    log_updated_seconds_ago: float | None
    production_active: bool
    wsl_sources_bytes: int | None
    recommended_next: str

    def to_dict(self) -> dict:
        return {
            "phase": self.phase,
            "sql_detail_present": self.sql_detail_present,
            "sql_detail_size_gb": round(self.sql_detail_size_gb, 3),
            "sql_download_pct": self.sql_download_pct,
            "download_speed": self.download_speed,
            "eta_seconds": self.eta_seconds,
            "eta_hours": round(self.eta_seconds / 3600, 1) if self.eta_seconds else None,
            "iids_output_csv": str(DEFAULT_IIDS_OUTPUT),
            "iids_output_rows": self.iids_output_rows,
            "log_path": self.log_path,
            "log_updated_seconds_ago": self.log_updated_seconds_ago,
            "production_active": self.production_active,
            "wsl_sources_bytes": self.wsl_sources_bytes,
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


def collect_production_status(*, sources_dir: Path | None = None) -> ProductionStatus:
    sources_dir = sources_dir or Path(os.environ.get("OPENXLAB_IIDS_SOURCES_DIR", "")).expanduser()
    if not str(sources_dir).strip():
        sources_dir = None

    detail, _ = find_iids_sql_paths(sources_dir) if sources_dir else (None, None)
    sql_gb = detail.stat().st_size / (1024**3) if detail and detail.exists() else 0.0
    output_rows = _file_rows(DEFAULT_IIDS_OUTPUT)

    log_age = _log_age_seconds(PRODUCTION_LOG)
    log_text = PRODUCTION_LOG.read_text(encoding="utf-8", errors="replace") if PRODUCTION_LOG.exists() else ""
    pct, speed, eta = _parse_log_progress(log_text)
    wsl_bytes = _wsl_sources_bytes()
    active = bool(log_age is not None and log_age < 300 and "Phase 1 complete" not in log_text)

    if output_rows >= 500:
        phase = "phase1_complete"
        nxt = "make atlas-iids-export-keys && acquire CNIPA/Lens geography for table_P9 keys"
    elif sql_gb >= IIDS_SQL_TARGET_GB * 0.99:
        phase = "convert_pending"
        nxt = "python scripts/64_run_atlas_iids_pipeline.py --skip-geo --production"
    elif detail and detail.exists() and sql_gb > 1:
        phase = "convert_pending"
        nxt = "Wait for SQL finalize, then run atlas-iids-pipeline --production --skip-geo"
    elif active or (pct is not None and pct < 99.9):
        phase = "sql_download"
        nxt = "Monitor: powershell -File scripts/windows_iids_external.ps1 -TargetDir D:\\iids_sources -Step status"
    elif "Phase 1 complete" in log_text:
        phase = "phase1_complete"
        nxt = "make atlas-iids-geo-build after CNIPA/Lens geography export arrives"
    else:
        phase = "not_started"
        nxt = (
            "powershell -File scripts/windows_iids_external.ps1 -TargetDir D:\\iids_sources -Step docs "
            "(then -Step detail). See docs/ATLAS_IIDS_CLEAN_RESTART_RUNBOOK.md"
        )

    if pct is None and wsl_bytes:
        pct = min(100.0, (wsl_bytes / (IIDS_SQL_TARGET_GB * 1024**3)) * 100)

    return ProductionStatus(
        phase=phase,
        sql_detail_present=bool(detail and detail.exists() and sql_gb > 0.5),
        sql_detail_size_gb=sql_gb if sql_gb else (wsl_bytes or 0) / (1024**3),
        sql_download_pct=round(pct, 2) if pct is not None else None,
        download_speed=speed,
        eta_seconds=eta,
        iids_output_rows=output_rows,
        log_path=str(PRODUCTION_LOG.relative_to(PROJECT_ROOT)),
        log_updated_seconds_ago=round(log_age, 1) if log_age is not None else None,
        production_active=active,
        wsl_sources_bytes=wsl_bytes,
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
