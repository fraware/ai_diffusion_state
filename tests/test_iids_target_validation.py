from __future__ import annotations

from pathlib import Path

import pytest

from diffusion_state.iids_paths import validate_production_target_dir


def test_rejects_wsl_home_path() -> None:
    issues = validate_production_target_dir(Path("/home/mateo/iids_sources"))
    assert any("WSL" in i for i in issues)


def test_accepts_external_drive_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    external = tmp_path / "iids_sources"
    external.mkdir()
    monkeypatch.setattr(
        "diffusion_state.iids_paths.shutil.disk_usage",
        lambda _p: type("U", (), {"free": 200 * 1024**3})(),
    )
    issues = validate_production_target_dir(external)
    assert not issues
