from __future__ import annotations

from diffusion_state.iids_paths import (
    IIDS_DETAIL_SQL_FILES,
    IIDS_DOC_FILES,
    IIDS_SQL_FILES,
    build_iids_download_argv,
    resolve_iids_download_targets,
)


def test_resolve_download_targets_defaults_to_docs_only() -> None:
    targets = resolve_iids_download_targets()
    assert "/base_patent_detail.sql" not in targets
    assert "/README.md" in targets


def test_resolve_download_targets_detail_only() -> None:
    targets = resolve_iids_download_targets(detail_only=True)
    assert targets == list(IIDS_DETAIL_SQL_FILES)


def test_resolve_download_targets_sql_only_includes_law_status() -> None:
    targets = resolve_iids_download_targets(sql_only=True)
    assert "/base_patent_detail.sql" in targets
    assert "/base_patent_law_status.sql" in targets
    assert "/README.md" not in targets


def test_resolve_download_targets_include_sql_adds_docs() -> None:
    targets = resolve_iids_download_targets(include_sql=True)
    assert "/README.md" in targets
    assert set(IIDS_SQL_FILES).issubset(set(targets))


def test_build_iids_download_argv_detail_only_by_default(tmp_path) -> None:
    cmd = build_iids_download_argv(tmp_path / "iids", python="python")
    assert "--detail-only" in cmd
    assert "--include-sql" not in cmd
    assert str(tmp_path / "iids") in cmd


def test_build_iids_download_argv_docs_only(tmp_path) -> None:
    cmd = build_iids_download_argv(tmp_path / "iids", python="python", docs_only=True)
    assert "--detail-only" not in cmd
    assert "--include-sql" not in cmd


def test_build_iids_download_argv_include_law_status(tmp_path) -> None:
    cmd = build_iids_download_argv(tmp_path / "iids", python="python", include_law_status=True)
    assert "--include-sql" in cmd
