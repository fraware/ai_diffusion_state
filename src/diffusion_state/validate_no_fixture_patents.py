from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from diffusion_state.utils import PROJECT_ROOT

RAW_PATENTS_DIR = PROJECT_ROOT / "data" / "raw" / "patents"
DEFAULT_RAW_FILE = RAW_PATENTS_DIR / "industrial_ai_patent_records.csv"
EVIDENCE_REPORT_PATH = PROJECT_ROOT / "paper" / "atlas_evidence_gate_report.json"

SEQUENTIAL_PATENT_ID = re.compile(r"^CN20\d{2}0{5,}\d+$", re.IGNORECASE)
REAL_SOURCE_FILE_PATTERNS = (
    re.compile(r"cnipa_industrial_ai", re.I),
    re.compile(r"lens_industrial_ai", re.I),
    re.compile(r"google_patents_industrial_ai", re.I),
    re.compile(r"cnki_", re.I),
    re.compile(r"csmar_", re.I),
)
TITLE_TEMPLATE = re.compile(r"^\d{4}年.+智能制造场景", re.UNICODE)
FIXTURE_SOURCE_VALUES = {"cnipa_micro_export", "fixture", "repository_fixture"}


def _load_patent_frames() -> tuple[pd.DataFrame, list[Path]]:
    paths: list[Path] = []
    frames: list[pd.DataFrame] = []
    if not RAW_PATENTS_DIR.exists():
        return pd.DataFrame(), paths
    for fp in sorted(RAW_PATENTS_DIR.glob("*.csv")):
        if fp.name.startswith("."):
            continue
        try:
            df = pd.read_csv(fp, low_memory=False)
        except Exception:
            continue
        if df.empty:
            continue
        df = df.copy()
        df["_source_file"] = fp.name
        frames.append(df)
        paths.append(fp)
    if not frames:
        return pd.DataFrame(), paths
    return pd.concat(frames, ignore_index=True), paths


def _has_documented_real_exports(raw_paths: list[Path]) -> bool:
    names = {p.name.lower() for p in raw_paths}
    return any(p.search(n) for p in REAL_SOURCE_FILE_PATTERNS for n in names)


def _detect_fixture_signals(df: pd.DataFrame) -> dict[str, bool | float]:
    if df.empty:
        return {
            "sequential_patent_ids": False,
            "synthetic_applicant_names": False,
            "single_fixture_source_file": False,
            "cnipa_micro_without_real_export": False,
            "systematic_title_templates": False,
            "abstract_equals_claims": False,
        }

    n = len(df)
    pid = df.get("patent_id", pd.Series(dtype=str)).astype(str)
    sequential_share = float(pid.str.match(SEQUENTIAL_PATENT_ID).mean()) if n else 0.0

    applicant = df.get("applicant_name", pd.Series(dtype=str)).astype(str)
    synth_share = float(applicant.str.contains("智造科技有限公司", regex=False).mean()) if n else 0.0

    src_file = df.get("source_url_or_file", pd.Series(dtype=str)).astype(str)
    unique_files = src_file.str.strip().nunique()
    only_fixture_file = (
        unique_files <= 1
        and src_file.str.contains("industrial_ai_patent_records.csv", regex=False).all()
    )

    source = df.get("source", pd.Series(dtype=str)).astype(str).str.strip().str.lower()
    cnipa_micro_share = float(source.isin({s.lower() for s in FIXTURE_SOURCE_VALUES}).mean())
    cnipa_micro_without_real = cnipa_micro_share > 0.5 and not _has_documented_real_exports(
        list(RAW_PATENTS_DIR.glob("*.csv"))
    )

    title = df.get("patent_title", pd.Series(dtype=str)).astype(str)
    title_template_share = float(title.str.match(TITLE_TEMPLATE).mean()) if n else 0.0

    abstract = df.get("abstract", pd.Series(dtype=str)).astype(str)
    claims = df.get("claims_or_description", pd.Series(dtype=str)).astype(str)
    equal_share = float((abstract == claims).mean()) if n else 0.0

    return {
        "sequential_patent_ids": sequential_share >= 0.5,
        "sequential_patent_id_share": sequential_share,
        "synthetic_applicant_names": synth_share >= 0.3,
        "synthetic_applicant_share": synth_share,
        "single_fixture_source_file": bool(only_fixture_file),
        "cnipa_micro_without_real_export": bool(cnipa_micro_without_real),
        "cnipa_micro_source_share": cnipa_micro_share,
        "systematic_title_templates": title_template_share >= 0.5,
        "title_template_share": title_template_share,
        "abstract_equals_claims": equal_share >= 0.8,
        "abstract_equals_claims_share": equal_share,
    }


def collect_evidence_gate_report(raw_path: Path | None = None) -> dict:
    raw_path = raw_path or DEFAULT_RAW_FILE
    df, raw_paths = _load_patent_frames()
    if df.empty and raw_path.exists():
        df = pd.read_csv(raw_path)
        df["_source_file"] = raw_path.name
        raw_paths = [raw_path]

    signals = _detect_fixture_signals(df)
    fixture_detected = any(
        signals.get(k)
        for k in (
            "sequential_patent_ids",
            "synthetic_applicant_names",
            "single_fixture_source_file",
            "cnipa_micro_without_real_export",
            "systematic_title_templates",
            "abstract_equals_claims",
        )
    )

    source_files = sorted({p.name for p in raw_paths})
    n_raw = int(len(df))
    n_unique = int(df["patent_id"].nunique()) if n_raw and "patent_id" in df.columns else 0

    real_export_files = [
        n
        for n in source_files
        if any(p.search(n) for p in REAL_SOURCE_FILE_PATTERNS)
    ]
    real_patent_source_present = bool(real_export_files) and not fixture_detected

    if not raw_paths:
        patent_source_status = "missing"
    elif fixture_detected and not real_export_files:
        patent_source_status = "fixture_micro"
    elif fixture_detected and real_export_files:
        patent_source_status = "mixed_fixture_and_real"
    elif real_patent_source_present:
        patent_source_status = "real_multi_source"
    else:
        patent_source_status = "unverified"

    return {
        "fixture_patents_detected": bool(fixture_detected),
        "real_patent_source_present": bool(real_patent_source_present),
        "n_raw_patent_records": n_raw,
        "n_unique_patent_ids": n_unique,
        "n_source_files": len(source_files),
        "source_files": source_files,
        "patent_source_status": patent_source_status,
        "fixture_signals": {k: v for k, v in signals.items()},
        "evidence_gate_passed": bool(not fixture_detected and real_patent_source_present),
    }


def write_evidence_gate_report(path: Path | None = None) -> dict:
    path = path or EVIDENCE_REPORT_PATH
    report = collect_evidence_gate_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


def validate_no_fixture_patents() -> tuple[bool, list[str]]:
    report = collect_evidence_gate_report()
    issues: list[str] = []
    if report["fixture_patents_detected"]:
        issues.append(
            f"fixture patent microdata detected ({report['patent_source_status']}); "
            "replace data/raw/patents/ with real CNIPA/Lens/Google exports"
        )
    if not report["real_patent_source_present"]:
        issues.append("no verified real patent export files in data/raw/patents/")
    if report["n_unique_patent_ids"] < 500 and not report["fixture_patents_detected"]:
        issues.append(
            f"n_unique_patent_ids={report['n_unique_patent_ids']} below minimum 500 for evidence-ready"
        )
    return len(issues) == 0, issues
