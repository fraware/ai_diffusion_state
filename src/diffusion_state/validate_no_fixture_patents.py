from __future__ import annotations

import re

import pandas as pd

from diffusion_state.patent_raw_sources import (
    FIXTURES_DIR,
    MANIFEST_PATH,
    RAW_PATENTS_DIR,
    list_evidence_patent_csv_files,
    list_fixture_patent_csv_files,
    relative_source_file,
)
from diffusion_state.utils import PROJECT_ROOT

EVIDENCE_REPORT_PATH = PROJECT_ROOT / "paper" / "atlas_evidence_gate_report.json"

SEQUENTIAL_PATENT_ID = re.compile(r"^CN20\d{2}0{5,}\d+$", re.IGNORECASE)
TITLE_TEMPLATE = re.compile(r"^\d{4}年.+智能制造场景", re.UNICODE)
FIXTURE_SOURCE_VALUES = {"cnipa_micro_export", "fixture", "repository_fixture", "quarantined"}


def _load_evidence_frames() -> tuple[pd.DataFrame, list]:
    paths = list_evidence_patent_csv_files()
    frames: list[pd.DataFrame] = []
    for fp in paths:
        try:
            df = pd.read_csv(fp, low_memory=False)
        except Exception:
            continue
        if df.empty:
            continue
        df = df.copy()
        df["_source_file"] = relative_source_file(fp)
        frames.append(df)
    if not frames:
        return pd.DataFrame(), paths
    return pd.concat(frames, ignore_index=True), paths


def _detect_fixture_signals(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "sequential_patent_ids": False,
            "sequential_patent_id_share": 0.0,
            "synthetic_applicant_names": False,
            "synthetic_applicant_share": 0.0,
            "single_fixture_source_file": False,
            "cnipa_micro_without_real_export": False,
            "cnipa_micro_source_share": 0.0,
            "systematic_title_templates": False,
            "title_template_share": 0.0,
            "abstract_equals_claims": False,
            "abstract_equals_claims_share": 0.0,
        }

    n = len(df)
    pid = df.get("patent_id", pd.Series(dtype=str)).astype(str)
    sequential_share = float(pid.str.match(SEQUENTIAL_PATENT_ID).mean()) if n else 0.0
    applicant = df.get("applicant_name", pd.Series(dtype=str)).astype(str)
    synth_share = float(applicant.str.contains("智造科技有限公司", regex=False).mean()) if n else 0.0
    src_file = df.get("source_url_or_file", pd.Series(dtype=str)).astype(str)
    only_fixture_file = (
        src_file.str.contains("fixtures/", regex=False).any()
        or src_file.str.contains("industrial_ai_patent_records.csv", regex=False).all()
    )
    source = df.get("source", pd.Series(dtype=str)).astype(str).str.strip().str.lower()
    cnipa_micro_share = float(source.isin({s.lower() for s in FIXTURE_SOURCE_VALUES}).mean())
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
        "cnipa_micro_without_real_export": cnipa_micro_share > 0.5,
        "cnipa_micro_source_share": cnipa_micro_share,
        "systematic_title_templates": title_template_share >= 0.5,
        "title_template_share": title_template_share,
        "abstract_equals_claims": equal_share >= 0.8,
        "abstract_equals_claims_share": equal_share,
    }


def collect_evidence_gate_report() -> dict:
    df, evidence_paths = _load_evidence_frames()
    fixture_paths = list_fixture_patent_csv_files()
    signals = _detect_fixture_signals(df)

    fixture_detected = bool(
        not evidence_paths
        or any(
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
    )

    source_files = sorted(relative_source_file(p) for p in evidence_paths)
    quarantined_files = sorted(relative_source_file(p) for p in fixture_paths)
    n_raw = int(len(df))
    n_unique = int(df["patent_id"].nunique()) if n_raw and "patent_id" in df.columns else 0

    real_patent_source_present = bool(evidence_paths) and not fixture_detected

    if not evidence_paths:
        patent_source_status = "missing_real_exports"
    elif fixture_detected:
        patent_source_status = "fixture_micro_in_evidence_path"
    else:
        patent_source_status = "real_multi_source"

    return {
        "fixture_patents_detected": bool(fixture_detected),
        "real_patent_source_present": bool(real_patent_source_present),
        "n_raw_patent_records": n_raw,
        "n_unique_patent_ids": n_unique,
        "n_source_files": len(source_files),
        "source_files": source_files,
        "quarantined_fixture_files": quarantined_files,
        "patent_source_status": patent_source_status,
        "manifest_path": str(MANIFEST_PATH.relative_to(PROJECT_ROOT)),
        "fixture_signals": signals,
        "evidence_gate_passed": bool(not fixture_detected and real_patent_source_present),
    }


def write_evidence_gate_report(path=None) -> dict:
    import json

    path = path or EVIDENCE_REPORT_PATH
    report = collect_evidence_gate_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


def validate_no_fixture_patents() -> tuple[bool, list[str]]:
    from diffusion_state.validate_patent_source_manifest import validate_patent_source_manifest

    report = collect_evidence_gate_report()
    issues: list[str] = []
    if report["fixture_patents_detected"]:
        issues.append(
            f"fixture or missing real patent exports ({report['patent_source_status']}); "
            "place manifest-backed exports under data/raw/patents/"
        )
    if not report["real_patent_source_present"]:
        issues.append("no verified real patent export files in evidence path")
    issues.extend(validate_patent_source_manifest())
    if report["n_unique_patent_ids"] < 500 and report["real_patent_source_present"]:
        issues.append(
            f"n_unique_patent_ids={report['n_unique_patent_ids']} below minimum 500 for evidence-ready"
        )
    return len(issues) == 0, issues
