from __future__ import annotations

from diffusion_state.iids_production_status import _parse_log_progress


def test_parse_log_progress_from_tail() -> None:
    log = (
        "noise\n"
        "[1. file: base_patent_detail.sql download info] File Progress: 0.18 % | "
        "Speed: 2.4 MB/s | Number of Workers: 8 | Time Elapsed: 91s | ETA: 57735.95s\n"
    )
    pct, speed, eta = _parse_log_progress(log)
    assert pct == 0.18
    assert "MB/s" in speed
    assert eta == 57735.95


def test_parse_log_progress_empty() -> None:
    assert _parse_log_progress("") == (None, "", None)
