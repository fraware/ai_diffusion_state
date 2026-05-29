from __future__ import annotations

from pathlib import Path

from diffusion_state.tiered_coverage_tables import compute_p14_rows, write_p14

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "iids_geography_sample.csv"


def test_compute_p14_on_fixture() -> None:
    rows, n_total = compute_p14_rows(FIXTURE)
    assert n_total == 2
    assert len(rows) >= 1
    assert sum(int(r["rows"]) for r in rows) == 2


def test_write_p14_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "p14.csv"
    rows, n_total = write_p14(FIXTURE, out)
    assert out.exists()
    assert n_total == 2
    assert rows
