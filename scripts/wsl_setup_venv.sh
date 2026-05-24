#!/usr/bin/env bash
set -euo pipefail
REPO="/mnt/c/Users/mateo/ai_diffusion_state"
cd "$REPO"
python3 -m venv .venv-wsl
.venv-wsl/bin/pip install -U pip
.venv-wsl/bin/pip install openxlab pandas pyarrow
.venv-wsl/bin/pip install -e ".[dev]"
.venv-wsl/bin/python -c "import openxlab, pandas; print('venv ready')"
