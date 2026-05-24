from __future__ import annotations

from pathlib import Path

import pytest

from diffusion_state.iids_paths import resolve_external_iids_target_dir


def test_resolve_external_returns_none_when_no_drives(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "exists", lambda self: False)
    assert resolve_external_iids_target_dir() is None


def test_resolve_external_prefers_first_drive_with_space(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_exists(self: Path) -> bool:
        s = str(self).upper()
        return s.startswith("D:") or s.startswith("E:")

    def fake_usage(path: Path) -> object:
        s = str(path).upper()
        free = 200 * 1024**3 if s.startswith("D:") else 10 * 1024**3
        return type("U", (), {"free": free})()

    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(
        "diffusion_state.iids_paths.shutil.disk_usage",
        fake_usage,
    )
    resolved = resolve_external_iids_target_dir()
    assert resolved is not None
    assert "iids_sources" in resolved.as_posix().lower()
    assert resolved.drive.upper().startswith("D")
