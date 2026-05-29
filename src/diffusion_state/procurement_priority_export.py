"""High-yield unresolved patent export for external geography procurement."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from diffusion_state.applicant_name_parsing import first_applicant_name

OUTPUT_COLUMNS = (
    "patent_id",
    "publication_number",
    "applicant_name",
    "application_year",
    "patent_title",
    "why_priority",
)

UNRESOLVED_CONF = "unresolved"


def _has_city(row: dict[str, str]) -> bool:
    return bool(str(row.get("applicant_city") or "").strip().replace("nan", ""))


def load_unresolved_patent_ids(geo_path: Path) -> set[str]:
    """Patent IDs with no city on the frozen geography file (canonical unresolved set)."""
    ids: set[str] = set()
    with geo_path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        for row in csv.DictReader(f):
            pid = str(row.get("patent_id") or row.get("publication_number") or "").strip()
            if not pid:
                continue
            conf = str(row.get("geo_match_confidence") or "").strip() or UNRESOLVED_CONF
            if conf == UNRESOLVED_CONF or not _has_city(row):
                ids.add(pid)
    return ids


def select_priority_applicants(
    counts: Counter[str],
    *,
    target_patents: int,
) -> dict[str, tuple[int, int]]:
    """first_applicant -> (rank, unresolved_count) until cumulative target."""
    selected: dict[str, tuple[int, int]] = {}
    cumulative = 0
    for rank, (name, cnt) in enumerate(counts.most_common(), start=1):
        if cumulative >= target_patents and rank > 1:
            break
        selected[name] = (rank, cnt)
        cumulative += cnt
    return selected


def export_procurement_priority(
    *,
    iids_csv: Path,
    geo_csv: Path,
    output_csv: Path,
    target_rows: int = 900_000,
) -> dict[str, int | str]:
    unresolved_ids = load_unresolved_patent_ids(geo_csv)
    counts: Counter[str] = Counter()
    n_scanned = 0

    with iids_csv.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            n_scanned += 1
            pid = str(row.get("patent_id") or "").strip()
            if pid not in unresolved_ids:
                continue
            app = str(row.get("applicant_name") or "")
            first = first_applicant_name(app) or "(blank)"
            counts[first] += 1

    priority_apps = select_priority_applicants(counts, target_patents=target_rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    n_written = 0

    with iids_csv.open("r", encoding="utf-8-sig", newline="") as fin, output_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as fout:
        writer = csv.DictWriter(fout, fieldnames=list(OUTPUT_COLUMNS))
        writer.writeheader()
        for row in csv.DictReader(fin):
            if n_written >= target_rows:
                break
            pid = str(row.get("patent_id") or "").strip()
            if pid not in unresolved_ids:
                continue
            app = str(row.get("applicant_name") or "")
            first = first_applicant_name(app) or "(blank)"
            if first not in priority_apps:
                continue
            rank, app_cnt = priority_apps[first]
            writer.writerow(
                {
                    "patent_id": pid,
                    "publication_number": str(row.get("publication_number") or pid),
                    "applicant_name": app,
                    "application_year": str(row.get("application_year") or ""),
                    "patent_title": str(row.get("patent_title") or ""),
                    "why_priority": (
                        f"unresolved_high_volume_applicant;rank={rank};"
                        f"applicant_unresolved_patents={app_cnt}"
                    ),
                }
            )
            n_written += 1

    return {
        "rows_scanned": n_scanned,
        "unresolved_ids_in_geo": len(unresolved_ids),
        "priority_applicants": len(priority_apps),
        "rows_written": n_written,
        "output": str(output_csv),
    }
