"""Atlas IIDS end-to-end workflow phases (cloud-first)."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from diffusion_state.iids_copyback import verify_copyback_artifacts
from diffusion_state.iids_geo_join import discover_geography_supplement, is_geography_template_path
from diffusion_state.iids_paths import (
    DEFAULT_IIDS_OUTPUT,
    FILTERED_PATENT_IDS_FOR_GEO_OUTPUT,
    MIN_SQL_DOWNLOAD_GB,
    resolve_external_iids_target_dir,
    resolve_iids_sources_dir,
)
from diffusion_state.iids_patent_converter import find_iids_sql_paths
from diffusion_state.patent_raw_sources import MANIFEST_PATH, RAW_PATENTS_DIR
from diffusion_state.utils import PROJECT_ROOT

WORKFLOW_JSON = PROJECT_ROOT / "outputs" / "tables" / "table_P8d_iids_workflow_status.json"

PhaseStatus = Literal["complete", "active", "blocked", "pending"]


class PhaseId(str, Enum):
    REPO_READY = "repo_ready"
    LAPTOP_PREFLIGHT = "laptop_preflight"
    CLOUD_PRODUCTION = "cloud_production"
    COPYBACK_IMPORTED = "copyback_imported"
    GEOGRAPHY_PROCUREMENT = "geography_procurement"
    EVIDENCE_CHAIN = "evidence_chain"
    ATLAS_EMPIRICAL = "atlas_empirical"


@dataclass(frozen=True)
class WorkflowPhase:
    id: PhaseId
    title: str
    status: PhaseStatus
    command: str
    detail: str
    blockers: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "title": self.title,
            "status": self.status,
            "command": self.command,
            "detail": self.detail,
            "blockers": list(self.blockers),
        }


def _repo_scripts_ready() -> bool:
    required = (
        PROJECT_ROOT / "scripts" / "cloud_iids_production.sh",
        PROJECT_ROOT / "scripts" / "cloud_iids_copyback.sh",
        PROJECT_ROOT / "scripts" / "70_verify_iids_copyback.py",
        PROJECT_ROOT / "src" / "diffusion_state" / "iids_copyback.py",
    )
    return all(p.exists() for p in required)


def _sql_rows(path: Path) -> int:
    if not path.exists():
        return 0
    import csv

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def collect_workflow_phases() -> list[WorkflowPhase]:
    phases: list[WorkflowPhase] = []
    blockers_global: list[str] = []

    repo_ok = _repo_scripts_ready()
    phases.append(
        WorkflowPhase(
            id=PhaseId.REPO_READY,
            title="Repository tooling",
            status="complete" if repo_ok else "blocked",
            command="git pull && git rev-parse HEAD",
            detail="Cloud scripts, copy-back verification, and workflow modules on main.",
            blockers=() if repo_ok else ("Missing cloud IIDS scripts — git pull origin main",),
        )
    )

    external = resolve_external_iids_target_dir()
    sources = resolve_iids_sources_dir()
    detail, _ = find_iids_sql_paths(sources)
    sql_gb = detail.stat().st_size / (1024**3) if detail and detail.exists() else 0.0
    iids_rows = _sql_rows(DEFAULT_IIDS_OUTPUT)
    creds = bool(os.environ.get("OPENXLAB_AK") and os.environ.get("OPENXLAB_SK"))

    try:
        import shutil

        free_sources = shutil.disk_usage(sources if sources.exists() else sources.parent).free / (1024**3)
    except OSError:
        free_sources = 0.0

    laptop_blockers: list[str] = []
    if not external and free_sources < MIN_SQL_DOWNLOAD_GB:
        laptop_blockers.append(
            f"Control laptop C: has ~{free_sources:.0f} GB free; do not download 136 GB SQL here."
        )

    phases.append(
        WorkflowPhase(
            id=PhaseId.LAPTOP_PREFLIGHT,
            title="Control laptop preflight",
            status="complete" if not laptop_blockers else "blocked",
            command="make atlas-iids-preflight && python scripts/50_atlas_status.py --json",
            detail=(
                "PCS + Atlas software ready; OpenXLAB credentials belong on the cloud VM, not necessarily here."
                if not laptop_blockers
                else "Resolve disk constraint before any local SQL download."
            ),
            blockers=tuple(laptop_blockers),
        )
    )

    cloud_complete = iids_rows >= 500
    cloud_active = bool(detail and detail.exists() and sql_gb > 1) or cloud_complete
    cloud_cmd = (
        "make atlas-iids-cloud-copyback  # after full-convert on VM"
        if cloud_complete
        else "make atlas-iids-cloud STEP=detail  # on 300 GB+ Ubuntu VM in tmux"
    )
    cloud_blockers: list[str] = []
    if not creds:
        cloud_blockers.append("OPENXLAB credentials required on cloud VM")
    if not cloud_complete and not cloud_active:
        cloud_blockers.append("Production not started on cloud VM")

    phases.append(
        WorkflowPhase(
            id=PhaseId.CLOUD_PRODUCTION,
            title="Cloud VM IIDS production",
            status="complete" if cloud_complete else ("active" if cloud_active else "pending"),
            command=cloud_cmd,
            detail=(
                f"SQL at {sources}: {sql_gb:.1f} GB; evidence CSV rows: {iids_rows}."
                if cloud_active or cloud_complete
                else "docs → detail → smoke-convert → full-convert on VM only."
            ),
            blockers=tuple(cloud_blockers) if not cloud_complete else (),
        )
    )

    copyback = verify_copyback_artifacts()
    phases.append(
        WorkflowPhase(
            id=PhaseId.COPYBACK_IMPORTED,
            title="Copy-back on control laptop",
            status="complete" if copyback.ready_for_geography_procurement else "pending",
            command="make atlas-iids-import-copyback ARCHIVE=atlas_iids_filtered_outputs.tar.gz",
            detail=f"IIDS rows: {copyback.iids_rows}; keys: {copyback.unique_patent_ids}.",
            blockers=tuple(copyback.blockers),
        )
    )

    geo = discover_geography_supplement(RAW_PATENTS_DIR)
    geo_ok = bool(geo and geo.exists() and not is_geography_template_path(geo))
    geo_blockers: list[str] = []
    if copyback.ready_for_geography_procurement and not geo_ok:
        geo_blockers.append(
            "Build data/raw/patents/cnipa_patent_geography_2015_2024.csv from "
            f"{FILTERED_PATENT_IDS_FOR_GEO_OUTPUT.name}"
        )
    elif geo and is_geography_template_path(geo):
        geo_blockers.append("Replace geography template with real CNIPA/Lens export")

    phases.append(
        WorkflowPhase(
            id=PhaseId.GEOGRAPHY_PROCUREMENT,
            title="Geography supplement (CNIPA/Lens)",
            status="complete" if geo_ok else ("active" if copyback.ready_for_geography_procurement else "pending"),
            command="make atlas-iids-geography-brief && make atlas-iids-geo-build",
            detail=str(geo) if geo_ok else "Targeted export for filtered patent IDs only.",
            blockers=tuple(geo_blockers),
        )
    )

    manifest_ok = MANIFEST_PATH.exists() and copyback.manifest_fill_me_count == 0
    evidence_ready = copyback.ready_for_evidence_chain and geo_ok and manifest_ok
    evidence_blockers = list(copyback.blockers)
    if not geo_ok:
        evidence_blockers.append("Geography supplement missing or template-only")
    if copyback.manifest_fill_me_count:
        evidence_blockers.append(
            f"Resolve {copyback.manifest_fill_me_count} FILL_ME field(s) in manifest draft"
        )

    phases.append(
        WorkflowPhase(
            id=PhaseId.EVIDENCE_CHAIN,
            title="Atlas evidence chain",
            status="complete" if evidence_ready else ("active" if geo_ok else "pending"),
            command="make atlas-iids-control-evidence-chain",
            detail="Runs geo join, manifest merge, atlas-evidence-check, patents, models.",
            blockers=tuple(evidence_blockers) if not evidence_ready else (),
        )
    )

    try:
        from diffusion_state.atlas_status import collect_atlas_status

        atlas = collect_atlas_status()
        empirical = bool(atlas.get("atlas_evidence_ready") and atlas.get("atlas_phase1_ready"))
    except Exception:
        empirical = False

    phases.append(
        WorkflowPhase(
            id=PhaseId.ATLAS_EMPIRICAL,
            title="Atlas empirical ready",
            status="complete" if empirical else "pending",
            command="python scripts/50_atlas_status.py --json --require-evidence",
            detail="atlas_evidence_ready=true; draft_atlas_v1.md may use real patent tables.",
            blockers=() if empirical else ("Complete evidence chain first",),
        )
    )

    return phases


def collect_workflow_report() -> dict:
    phases = collect_workflow_phases()
    active = next((p for p in phases if p.status == "active"), None)
    blocked = [p for p in phases if p.status == "blocked"]
    complete = [p for p in phases if p.status == "complete"]
    next_phase = active or next((p for p in phases if p.status == "pending"), phases[-1])

    return {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "canonical_host": "cloud_vm",
        "phases_complete": len(complete),
        "phases_total": len(phases),
        "next_phase_id": next_phase.id.value,
        "next_command": next_phase.command,
        "active_phase_id": active.id.value if active else "",
        "blocked_phase_ids": [p.id.value for p in blocked],
        "phases": [p.to_dict() for p in phases],
    }


def write_workflow_report() -> dict:
    report = collect_workflow_report()
    WORKFLOW_JSON.parent.mkdir(parents=True, exist_ok=True)
    WORKFLOW_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
