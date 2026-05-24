from __future__ import annotations

from diffusion_state.iids_paths import MIN_SQL_DOWNLOAD_GB, resolve_iids_sources_dir


def test_resolve_sources_dir_env_override(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENXLAB_IIDS_SOURCES_DIR", str(tmp_path / "external_iids"))
    assert resolve_iids_sources_dir() == (tmp_path / "external_iids").resolve()


def test_min_sql_download_threshold() -> None:
    assert MIN_SQL_DOWNLOAD_GB >= 150
