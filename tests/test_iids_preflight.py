from __future__ import annotations

from diffusion_state.patent_raw_sources import RAW_PATENTS_DIR


def test_cnipa_or_lens_exports_excludes_template_only() -> None:
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "preflight",
        Path("scripts/67_atlas_iids_preflight.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    template = RAW_PATENTS_DIR / "cnipa_patent_geography_template.csv"
    assert template.exists()
    assert mod._cnipa_or_lens_exports_present() is False
