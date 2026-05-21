from __future__ import annotations

from diffusion_state.sync_paper_stats import (
    build_hub_exclusion_markdown,
    build_model1_line,
    sync_results_memo,
)
from diffusion_state.utils import PROJECT_ROOT


def test_hub_markdown_uses_table6_when_present():
    t6 = PROJECT_ROOT / "outputs" / "tables" / "table_6_hub_exclusion_robustness.csv"
    if not t6.exists():
        return
    md = build_hub_exclusion_markdown()
    assert "Full sample" in md
    assert "|" in md
    assert "4." in md or "3." in md


def test_sync_results_memo_roundtrip():
    path = PROJECT_ROOT / "paper" / "results_memo.md"
    if not path.exists():
        return
    before = path.read_text(encoding="utf-8")
    sync_results_memo(path)
    after = path.read_text(encoding="utf-8")
    assert "<!-- PCS:HUB_TABLE -->" in after
    t6 = PROJECT_ROOT / "outputs" / "tables" / "table_6_hub_exclusion_robustness.csv"
    if t6.exists():
        line = build_model1_line()
        assert line in after or "**Model 1:**" in after
    path.write_text(before, encoding="utf-8")
