"""Dump raw Lens API payloads and party-field audit for geography smoke diagnostics."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "lens_export",
    ROOT / "scripts" / "79_lens_geography_export.py",
)
lens_export = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(lens_export)

DEFAULT_INCLUDE = [
    "lens_id",
    "jurisdiction",
    "doc_number",
    "kind",
    "doc_key",
    "date_published",
    "biblio",
]

EXTENDED_INCLUDE = [
    "lens_id",
    "jurisdiction",
    "doc_number",
    "kind",
    "doc_key",
    "biblio",
    "biblio.parties",
    "applicant.address",
    "applicant.name",
    "applicant.residence",
    "owner_all.address",
    "inventor.address",
    "agent.address",
]

AUDIT_COLUMNS = [
    "patent_id",
    "lens_id",
    "doc_key",
    "query_mode",
    "has_applicants",
    "applicant_name",
    "applicant_residence",
    "applicant_extracted_address",
    "has_inventors",
    "inventor_extracted_address",
    "has_owners_all",
    "owner_extracted_address",
    "has_agents",
    "agent_extracted_address",
    "top_level_address_fields",
    "raw_party_keys",
]


def _text_field(obj: dict[str, Any] | None, key: str) -> str:
    if not isinstance(obj, dict):
        return ""
    val = obj.get(key)
    if isinstance(val, dict):
        return str(val.get("value") or "").strip()
    return str(val or "").strip()


def _first_party(parties: dict[str, Any], group: str) -> dict[str, Any]:
    items = parties.get(group)
    if not isinstance(items, list) or not items:
        return {}
    first = items[0]
    return first if isinstance(first, dict) else {}


def _party_keys(parties: dict[str, Any]) -> str:
    if not isinstance(parties, dict):
        return ""
    summary: dict[str, list[str]] = {}
    for group, items in parties.items():
        if not isinstance(items, list) or not items:
            summary[group] = []
            continue
        keys: set[str] = set()
        for item in items[:3]:
            if isinstance(item, dict):
                keys.update(item.keys())
        summary[group] = sorted(keys)
    return json.dumps(summary, ensure_ascii=False)


def _top_level_address_keys(record: dict[str, Any]) -> str:
    hits: list[str] = []

    def walk(obj: Any, prefix: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                path = f"{prefix}.{k}" if prefix else k
                if "address" in k.lower() or "residence" in k.lower():
                    text = _text_field(obj, k) if isinstance(v, (str, dict)) else ""
                    if not text and isinstance(v, str):
                        text = v.strip()
                    if text:
                        hits.append(path)
                walk(v, path)
        elif isinstance(obj, list) and obj and prefix.count(".") < 6:
            walk(obj[0], prefix)

    walk(record, "")
    return "|".join(sorted(set(hits)))


def _match_input_id(
    record: dict[str, Any],
    input_by_norm: dict[str, str],
) -> str:
    cands = lens_export.candidate_ids(record)
    for c in cands:
        if c in input_by_norm:
            return input_by_norm[c]
    joined = " ".join(cands)
    for k, original in input_by_norm.items():
        if k and k in joined:
            return original
    return ""


def audit_row(
    patent_id: str,
    record: dict[str, Any],
    *,
    query_mode: str,
) -> dict[str, str]:
    parties = lens_export.get_path(record, ["biblio", "parties"], {})
    if not isinstance(parties, dict):
        parties = {}

    applicant = _first_party(parties, "applicants")
    inventor = _first_party(parties, "inventors")
    owner = _first_party(parties, "owners_all")
    agent = _first_party(parties, "agents")

    return {
        "patent_id": patent_id,
        "lens_id": str(record.get("lens_id") or ""),
        "doc_key": str(record.get("doc_key") or ""),
        "query_mode": query_mode,
        "has_applicants": str(bool(parties.get("applicants"))),
        "applicant_name": _text_field(applicant, "extracted_name"),
        "applicant_residence": _text_field(applicant, "residence"),
        "applicant_extracted_address": _text_field(applicant, "extracted_address")
        or _text_field(applicant, "address"),
        "has_inventors": str(bool(parties.get("inventors"))),
        "inventor_extracted_address": _text_field(inventor, "extracted_address")
        or _text_field(inventor, "address"),
        "has_owners_all": str(bool(parties.get("owners_all"))),
        "owner_extracted_address": _text_field(owner, "extracted_address")
        or _text_field(owner, "address"),
        "has_agents": str(bool(parties.get("agents"))),
        "agent_extracted_address": _text_field(agent, "extracted_address")
        or _text_field(agent, "address"),
        "top_level_address_fields": _top_level_address_keys(record),
        "raw_party_keys": _party_keys(parties),
    }


def run_diagnostic(
    *,
    token: str,
    ids: list[str],
    query_mode: str,
    include: list[str] | None,  # None = omit include (full record projection)
    chunk_size: int,
    sleep: float,
    timeout: int,
    verify_ssl: bool,
    output_jsonl: Path,
    output_audit: Path,
) -> dict[str, int]:
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    output_audit.parent.mkdir(parents=True, exist_ok=True)

    audit_rows: list[dict[str, str]] = []
    n_records = 0

    with output_jsonl.open("w", encoding="utf-8") as jf:
        for batch_no, id_chunk in enumerate(
            lens_export.chunks(ids, chunk_size), start=1
        ):
            input_by_norm = {lens_export.norm_id(x): x for x in id_chunk}
            try:
                data = lens_export.lens_request(
                    token,
                    id_chunk,
                    include,
                    timeout,
                    sleep,
                    verify_ssl=verify_ssl,
                )
            except Exception as exc:
                print(
                    {"query_mode": query_mode, "batch_no": batch_no, "error": str(exc)},
                    file=sys.stderr,
                    flush=True,
                )
                raise
            records = data.get("data") or []
            n_records += len(records)

            matched_inputs: set[str] = set()
            for rec in records:
                patent_id = _match_input_id(rec, input_by_norm)
                if not patent_id:
                    patent_id = str(rec.get("doc_key") or rec.get("lens_id") or "")
                if patent_id:
                    matched_inputs.add(lens_export.norm_id(patent_id))

                line = {
                    "query_mode": query_mode,
                    "batch_no": batch_no,
                    "patent_id": patent_id,
                    "record": rec,
                }
                jf.write(json.dumps(line, ensure_ascii=False) + "\n")
                audit_rows.append(audit_row(patent_id, rec, query_mode=query_mode))

            for k, original in input_by_norm.items():
                if k not in matched_inputs:
                    audit_rows.append({
                        "patent_id": original,
                        "lens_id": "",
                        "doc_key": "",
                        "query_mode": query_mode,
                        "has_applicants": "False",
                        "applicant_name": "",
                        "applicant_residence": "",
                        "applicant_extracted_address": "",
                        "has_inventors": "False",
                        "inventor_extracted_address": "",
                        "has_owners_all": "False",
                        "owner_extracted_address": "",
                        "has_agents": "False",
                        "agent_extracted_address": "",
                        "top_level_address_fields": "",
                        "raw_party_keys": "",
                    })

    with output_audit.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(audit_rows)

    return {"input_ids": len(ids), "lens_records": n_records, "audit_rows": len(audit_rows)}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Lens raw JSON + party-field audit for smoke diagnostics.",
    )
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-jsonl", required=True, type=Path)
    ap.add_argument("--output-audit", required=True, type=Path)
    ap.add_argument(
        "--query-mode",
        choices=("default", "extended", "full"),
        default="default",
        help="default=biblio include; extended=projection test; full=no include filter",
    )
    ap.add_argument("--chunk-size", type=int, default=25)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--token-env", default="LENS_API_TOKEN")
    ap.add_argument("--insecure-ssl", action="store_true")
    ap.add_argument(
        "--also-run-extended",
        action="store_true",
        help="After default/full run, also write *_projection audit/jsonl (extended include)",
    )
    args = ap.parse_args()

    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit(f"Missing ${args.token_env}")

    ids = lens_export.read_ids(args.input)
    if not ids:
        raise SystemExit(f"No IDs found in {args.input}")

    verify_ssl = lens_export._ssl_verify(args.insecure_ssl)

    if args.query_mode == "extended":
        include: list[str] | None = EXTENDED_INCLUDE
    elif args.query_mode == "full":
        include = None
    else:
        include = DEFAULT_INCLUDE

    stats = run_diagnostic(
        token=token,
        ids=ids,
        query_mode=args.query_mode,
        include=include,
        chunk_size=args.chunk_size,
        sleep=args.sleep,
        timeout=args.timeout,
        verify_ssl=verify_ssl,
        output_jsonl=args.output_jsonl,
        output_audit=args.output_audit,
    )
    print(stats)

    if args.query_mode == "full":
        # full = omit include key from request body
        body_include_sent = "OMITTED"
    else:
        body_include_sent = include
    print({"query_mode": args.query_mode, "include_sent": body_include_sent})

    if args.also_run_extended and args.query_mode != "extended":
        ext_jsonl = args.output_jsonl.with_name(
            args.output_jsonl.stem + "_projection.jsonl"
        )
        ext_audit = args.output_audit.with_name(
            args.output_audit.stem + "_projection.csv"
        )
        ext_stats = run_diagnostic(
            token=token,
            ids=ids,
            query_mode="extended",
            include=EXTENDED_INCLUDE,
            chunk_size=args.chunk_size,
            sleep=args.sleep,
            timeout=args.timeout,
            verify_ssl=verify_ssl,
            output_jsonl=ext_jsonl,
            output_audit=ext_audit,
        )
        print({"extended_projection": ext_stats})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
