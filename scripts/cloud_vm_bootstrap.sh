#!/usr/bin/env bash
# One-shot bootstrap for a fresh Ubuntu 22.04/24.04 cloud VM (300 GB+ disk).
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/fraware/ai_diffusion_state.git}"
REPO_DIR="${REPO_DIR:-$HOME/ai_diffusion_state}"
IIDS_MOUNT="${OPENXLAB_IIDS_SOURCES_DIR:-/mnt/iids_sources}"

echo "=== Atlas IIDS cloud VM bootstrap ==="

sudo apt-get update
sudo apt-get install -y git python3-venv python3-pip tmux htop unzip rsync curl

if [[ ! -d "$REPO_DIR/.git" ]]; then
  git clone "$REPO_URL" "$REPO_DIR"
fi
cd "$REPO_DIR"
git pull

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip wheel
pip install -e .[dev] || pip install pandas openpyxl statsmodels requests beautifulsoup4 openxlab

sudo mkdir -p "$IIDS_MOUNT"
sudo chown -R "$USER:$USER" "$IIDS_MOUNT"

export OPENXLAB_IIDS_SOURCES_DIR="$IIDS_MOUNT"
export OPENXLAB_INSECURE_SSL="${OPENXLAB_INSECURE_SSL:-1}"
export PYTHONUTF8=1

if [[ -z "${OPENXLAB_AK:-}" || -z "${OPENXLAB_SK:-}" ]]; then
  echo ""
  echo "WARN: set OPENXLAB_AK and OPENXLAB_SK before production download."
  echo "  export OPENXLAB_AK=..."
  echo "  export OPENXLAB_SK=..."
fi

python scripts/72_atlas_iids_workflow_status.py
df -h "$IIDS_MOUNT" | tail -1 || df -h / | tail -1

cat <<EOF

Bootstrap complete.

Start production in tmux:
  cd $REPO_DIR
  source .venv/bin/activate
  tmux new -s iids
  make atlas-iids-cloud STEP=status
  make atlas-iids-cloud STEP=docs
  make atlas-iids-cloud STEP=detail
  make atlas-iids-cloud STEP=smoke-convert
  make atlas-iids-cloud STEP=full-convert
  make atlas-iids-cloud-copyback

EOF
