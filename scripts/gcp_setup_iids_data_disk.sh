#!/usr/bin/env bash
# Format and mount the GCE data disk at /mnt/iids_sources (run on the VM with sudo).
set -euo pipefail

MOUNT="${OPENXLAB_IIDS_SOURCES_DIR:-/mnt/iids_sources}"
MIN_GB=300

echo "=== GCP IIDS data disk setup -> $MOUNT ==="

if mountpoint -q "$MOUNT" 2>/dev/null; then
  free_gb=$(df -BG "$MOUNT" | awk 'NR==2 {gsub(/G/,"",$4); print $4}')
  echo "Already mounted: $MOUNT (${free_gb}G free)"
  if [[ "${free_gb:-0}" -lt "$MIN_GB" ]]; then
    echo "ERROR: need >= ${MIN_GB} GB free at $MOUNT" >&2
    exit 2
  fi
  exit 0
fi

# Find unformatted or empty data disk (skip root)
DEVICE=""
for cand in /dev/disk/by-id/google-iids-data /dev/sdb /dev/nvme0n2; do
  if [[ -b "$cand" ]]; then
    DEVICE="$cand"
    break
  fi
done

if [[ -z "$DEVICE" ]]; then
  echo "Searching for unmounted block device > 100G ..."
  while read -r name size type mount; do
    [[ "$type" == "disk" ]] || continue
    [[ "$mount" == "0" ]] || continue
    size_g=${size%G}
    if [[ "${size_g%%.*}" -ge 100 ]]; then
      DEVICE="/dev/$name"
      break
    fi
  done < <(lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | tail -n +2)
fi

if [[ -z "$DEVICE" ]]; then
  echo "ERROR: no unattached data disk found. Attach a 500 GB disk in GCE first." >&2
  echo "See docs/ATLAS_IIDS_GCP_VM_SETUP.md" >&2
  exit 2
fi

echo "Using device: $DEVICE"
if ! blkid "$DEVICE" &>/dev/null; then
  echo "Creating ext4 on $DEVICE ..."
  mkfs.ext4 -F "$DEVICE"
fi

mkdir -p "$MOUNT"
if ! grep -q "$MOUNT" /etc/fstab 2>/dev/null; then
  uuid=$(blkid -s UUID -o value "$DEVICE")
  echo "UUID=$uuid $MOUNT ext4 defaults,nofail 0 2" >> /etc/fstab
fi

mount -a || mount "$DEVICE" "$MOUNT"
chown -R "${SUDO_USER:-$USER}:${SUDO_USER:-$USER}" "$MOUNT"

df -h "$MOUNT"
free_gb=$(df -BG "$MOUNT" | awk 'NR==2 {gsub(/G/,"",$4); print $4}')
if [[ "${free_gb:-0}" -lt "$MIN_GB" ]]; then
  echo "ERROR: $MOUNT has only ${free_gb}G free; need >= ${MIN_GB}G" >&2
  exit 2
fi

echo "OK: $MOUNT ready with ${free_gb}G free"
