#!/usr/bin/env bash
# GCE preflight: RAM, vCPU, and /mnt/iids_sources disk before IIDS download.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MOUNT="${OPENXLAB_IIDS_SOURCES_DIR:-/mnt/iids_sources}"
MIN_DISK_GB=300
MIN_RAM_GB=16
MIN_VCPU=4

cd "$REPO"
PYTHON="${PYTHON:-python3}"

echo "=== GCP VM IIDS preflight ==="
echo "Host: $(hostname)"
echo "OS: $(. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME" || uname -a)"

vcpu=$(nproc 2>/dev/null || echo 0)
ram_gb=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)

echo "vCPU: $vcpu (want >= $MIN_VCPU; recommend 8+)"
echo "RAM: ${ram_gb} GB (want >= ${MIN_RAM_GB} GB; recommend 32 GB)"

issues=0
if [[ "$vcpu" -lt "$MIN_VCPU" ]]; then
  echo "BLOCKER: too few vCPUs for SQL convert — resize to e2-standard-8 or larger" >&2
  issues=1
fi
if [[ "$ram_gb" -lt "$MIN_RAM_GB" ]]; then
  echo "BLOCKER: too little RAM — resize machine type (e2-medium is insufficient)" >&2
  issues=1
fi

if [[ ! -d "$MOUNT" ]]; then
  echo "BLOCKER: $MOUNT missing — run: sudo bash scripts/gcp_setup_iids_data_disk.sh" >&2
  issues=1
else
  df -h "$MOUNT" || true
  free_gb=$(df -BG "$MOUNT" 2>/dev/null | awk 'NR==2 {gsub(/G/,"",$4); print $4}' || echo 0)
  echo "Free at $MOUNT: ${free_gb} GB (need >= $MIN_DISK_GB)"
  if [[ "${free_gb:-0}" -lt "$MIN_DISK_GB" ]]; then
    echo "BLOCKER: attach 500 GB data disk per docs/ATLAS_IIDS_GCP_VM_SETUP.md" >&2
    issues=1
  fi
fi

root_free=$(df -BG / | awk 'NR==2 {gsub(/G/,"",$4); print $4}')
echo "Root / free: ${root_free} GB (repo + venv only; do not download SQL here)"

if [[ -z "${OPENXLAB_AK:-}" || -z "${OPENXLAB_SK:-}" ]]; then
  echo "BLOCKER: export OPENXLAB_AK and OPENXLAB_SK on this VM" >&2
  issues=1
fi

if [[ "$issues" -ne 0 ]]; then
  exit 2
fi

"$PYTHON" scripts/72_atlas_iids_workflow_status.py
echo "OK: GCP VM ready for make atlas-iids-cloud STEP=docs"
