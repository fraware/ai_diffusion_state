from __future__ import annotations

from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, write_csv


def build_china_export_outcomes(baci_dir: Path, out_path: Path | None = None, china_code: int = 156) -> pd.DataFrame:
    """Build China HS6 export outcomes from downloaded BACI yearly files.

    BACI columns: t, i, j, k, v, q
    v is thousands current USD. q is metric tons. Country codes are numeric BACI/Comtrade codes.
    """
    out_path = out_path or PROJECT_ROOT / "data" / "processed" / "baci_china_hs6_exports.csv"
    files = sorted(Path(baci_dir).glob("BACI_HS*_Y*_V*.csv"))
    if not files:
        raise FileNotFoundError(f"No BACI files found in {baci_dir}")
    frames = []
    for f in files:
        df = pd.read_csv(f, dtype={"k": str})
        df = df[df["i"] == china_code].copy()
        df["source_file"] = f.name
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["unit_value_usd_per_ton"] = (out["v"] * 1000) / out["q"].replace({0: pd.NA})
    out = out.groupby(["t", "k"], as_index=False).agg(
        export_value_thousand_usd=("v", "sum"),
        quantity_tons=("q", "sum"),
    )
    out["unit_value_usd_per_ton"] = (out["export_value_thousand_usd"] * 1000) / out["quantity_tons"].replace({0: pd.NA})
    out = out.sort_values(["k", "t"])
    out["export_value_growth"] = out.groupby("k")["export_value_thousand_usd"].pct_change()
    out["unit_value_growth"] = out.groupby("k")["unit_value_usd_per_ton"].pct_change()
    write_csv(out, out_path)
    return out


if __name__ == "__main__":
    import os
    baci_dir = Path(os.environ.get("BACI_DIR", PROJECT_ROOT / "data" / "raw" / "baci"))
    build_china_export_outcomes(baci_dir)
