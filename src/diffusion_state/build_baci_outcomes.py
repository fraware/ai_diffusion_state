from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from diffusion_state.utils import PROJECT_ROOT, read_yaml, write_csv

CHINA_CODE = 156
BACI_QUANTITY_UNIT = "metric_ton"
TARGET_YEARS = list(range(2017, 2025))


def _require_baci_files(baci_dir: Path) -> list[Path]:
    files = sorted(baci_dir.glob("BACI_HS17_Y*_V*.csv"))
    if not files:
        raise FileNotFoundError(
            f"No BACI HS17 yearly CSV files in {baci_dir}. Run:\n"
            f"  python -c \"from diffusion_state.fetch_baci import fetch_baci_hs17; fetch_baci_hs17()\"\n"
            f"or place CEPII files from {BACI_HS17_ZIP_URL_HINT} manually."
        )
    return files


BACI_HS17_ZIP_URL_HINT = "https://www.cepii.fr/DATA_DOWNLOAD/baci/data/BACI_HS17_V202601.zip"


def _year_from_filename(path: Path) -> int:
    # BACI_HS17_Y2023_V202601.csv
    stem = path.stem
    part = stem.split("_Y")[1].split("_")[0]
    return int(part)


def build_china_hs6_year_from_file(path: Path, china_code: int = CHINA_CODE) -> pd.DataFrame:
    """One BACI year file: China exports and world exports by HS6."""
    df = pd.read_csv(
        path,
        usecols=["t", "k", "i", "j", "v", "q"],
        dtype={"k": str, "i": int, "j": int, "t": int},
    )
    year = int(df["t"].iloc[0])
    if year not in TARGET_YEARS:
        return pd.DataFrame()

    df["hs6"] = df["k"].astype(str).str.zfill(6)
    df["export_value_usd"] = df["v"] * 1000
    df["quantity"] = df["q"]

    world = (
        df.groupby("hs6", as_index=False)
        .agg(
            world_export_value_usd=("export_value_usd", "sum"),
            world_quantity=("quantity", "sum"),
        )
    )
    china = df[df["i"] == china_code]
    china_agg = (
        china.groupby("hs6", as_index=False)
        .agg(
            export_value_usd=("export_value_usd", "sum"),
            quantity=("quantity", "sum"),
            num_destinations=("j", "nunique"),
        )
    )
    out = china_agg.merge(world, on="hs6", how="left")
    out["year"] = year
    out["unit"] = BACI_QUANTITY_UNIT
    out["unit_value"] = np.where(out["quantity"] > 0, out["export_value_usd"] / out["quantity"], np.nan)
    out["china_world_market_share"] = np.where(
        out["world_export_value_usd"] > 0,
        out["export_value_usd"] / out["world_export_value_usd"],
        np.nan,
    )
    return out


def build_export_outcomes_hs6_year(baci_dir: Path, china_code: int = CHINA_CODE) -> pd.DataFrame:
    frames = []
    for f in _require_baci_files(baci_dir):
        chunk = build_china_hs6_year_from_file(f, china_code=china_code)
        if not chunk.empty:
            frames.append(chunk)
    if not frames:
        raise ValueError(f"No HS6 outcomes for years {TARGET_YEARS}")
    hs6 = pd.concat(frames, ignore_index=True)
    hs6 = hs6.sort_values(["hs6", "year"])
    for col in ["export_value_usd", "quantity"]:
        if (hs6[col] < 0).any():
            raise ValueError(f"Negative values in {col}")

    hs6["export_value_growth"] = hs6.groupby("hs6")["export_value_usd"].transform(lambda s: np.log(s).diff())
    hs6["quantity_growth"] = hs6.groupby("hs6")["quantity"].transform(
        lambda s: np.log(s.replace(0, np.nan)).diff()
    )
    hs6["unit_value_growth"] = hs6.groupby("hs6")["unit_value"].transform(
        lambda s: np.log(s).diff()
    )
    return hs6[
        [
            "year",
            "hs6",
            "export_value_usd",
            "quantity",
            "unit",
            "unit_value",
            "export_value_growth",
            "quantity_growth",
            "unit_value_growth",
            "num_destinations",
            "world_export_value_usd",
            "china_world_market_share",
        ]
    ]


def build_hs_bridge_table() -> pd.DataFrame:
    cfg = read_yaml(PROJECT_ROOT / "configs" / "hs_smart_factory_bridge.yml")
    rows = []
    for i, row in enumerate(cfg.get("bridges", []), start=1):
        rows.append(
            {
                "bridge_id": f"bridge_{i:03d}",
                "smart_factory_industry_code": row["smart_factory_industry_code"],
                "smart_factory_industry_label": row["smart_factory_industry_label"],
                "hs_level": row["hs_level"],
                "hs_code": str(row["hs_code"]),
                "hs_description": row["hs_description"],
                "mapping_confidence": row["mapping_confidence"],
                "mapping_reason": row["mapping_reason"],
                "source_or_method": row["source_or_method"],
            }
        )
    bridge = pd.DataFrame(rows)
    write_csv(bridge, PROJECT_ROOT / "data" / "processed" / "hs_to_smart_factory_sector_bridge.csv")
    return bridge


def _hs6_matches_code(hs6: str, hs_level: str, hs_code: str) -> bool:
    if hs_level == "HS2":
        return hs6.startswith(hs_code.zfill(2))
    if hs_level == "HS4":
        return hs6.startswith(hs_code.zfill(4))
    if hs_level == "HS6":
        return hs6 == hs_code.zfill(6)
    return False


def _sector_hs_mask(hs6_codes: pd.Series, bridge_rows: pd.DataFrame) -> pd.Series:
    mask = pd.Series(False, index=hs6_codes.index)
    for _, brow in bridge_rows.iterrows():
        mask |= hs6_codes.map(
            lambda h, lvl=brow["hs_level"], code=brow["hs_code"]: _hs6_matches_code(h, lvl, code)
        )
    return mask


def build_export_outcomes_sector_year(
    hs6: pd.DataFrame, bridge: pd.DataFrame
) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    for sector_code, brow in bridge.groupby("smart_factory_industry_code"):
        mask = _sector_hs_mask(hs6["hs6"], brow)
        sub = hs6[mask]
        if sub.empty:
            continue
        agg = (
            sub.groupby("year", as_index=False)
            .agg(
                export_value_usd=("export_value_usd", "sum"),
                quantity=("quantity", "sum"),
                china_export=("export_value_usd", "sum"),
                world_export=("world_export_value_usd", "sum"),
                hs6_count=("hs6", "nunique"),
                quantity_available_share=(
                    "quantity",
                    lambda s: float((s > 0).mean()),
                ),
            )
        )
        agg["sector_code"] = sector_code
        agg["sector_label"] = brow["smart_factory_industry_label"].iloc[0]
        confs = set(brow["mapping_confidence"])
        if "high" in confs:
            summary_conf = "high"
        elif "medium" in confs:
            summary_conf = "medium"
        else:
            summary_conf = "low"
        agg["mapping_confidence_summary"] = summary_conf
        records.append(agg)

    if not records:
        raise ValueError("No HS6 rows matched the smart-factory sector bridge")

    sector = pd.concat(records, ignore_index=True).sort_values(["sector_code", "year"])
    sector["china_world_market_share"] = np.where(
        sector["world_export"] > 0,
        sector["china_export"] / sector["world_export"],
        np.nan,
    )
    sector = sector.drop(columns=["china_export", "world_export"])
    sector["unit_value_index"] = sector.groupby("sector_code")["export_value_usd"].transform(
        lambda s: s / s.iloc[0] if len(s) > 0 and s.iloc[0] > 0 else np.nan
    )
    sector["export_value_growth"] = sector.groupby("sector_code")["export_value_usd"].transform(
        lambda s: np.log(s).diff()
    )
    sector["unit_value_growth"] = sector.groupby("sector_code")["unit_value_index"].transform(
        lambda s: np.log(s).diff()
    )
    return sector[
        [
            "year",
            "sector_code",
            "sector_label",
            "export_value_usd",
            "quantity_available_share",
            "unit_value_index",
            "export_value_growth",
            "unit_value_growth",
            "china_world_market_share",
            "hs6_count",
            "mapping_confidence_summary",
        ]
    ]


def build_china_hs6_interim(hs6: pd.DataFrame, out_path: Path) -> pd.DataFrame:
    """Long-format China export flows are not stored in interim; write HS6-year summary."""
    write_csv(hs6, out_path)
    return hs6


def build_china_export_outcomes(
    baci_dir: Path | None = None,
    interim_path: Path | None = None,
    hs6_path: Path | None = None,
    sector_path: Path | None = None,
    china_code: int = CHINA_CODE,
) -> pd.DataFrame:
    baci_dir = baci_dir or Path(os.environ.get("BACI_DIR", PROJECT_ROOT / "data" / "raw" / "baci"))
    interim_path = interim_path or PROJECT_ROOT / "data" / "interim" / "baci_china_hs6_year.csv"
    hs6_path = hs6_path or PROJECT_ROOT / "data" / "processed" / "export_outcomes_hs6_year.csv"
    sector_path = sector_path or PROJECT_ROOT / "data" / "processed" / "export_outcomes_sector_year.csv"

    hs6 = build_export_outcomes_hs6_year(baci_dir, china_code=china_code)
    build_china_hs6_interim(hs6, interim_path)
    write_csv(hs6, hs6_path)

    bridge = build_hs_bridge_table()
    sector = build_export_outcomes_sector_year(hs6, bridge)
    write_csv(sector, sector_path)
    return hs6


if __name__ == "__main__":
    build_china_export_outcomes()
