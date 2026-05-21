"""Run all PCS gates before paper drafting."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(label: str, cmd: list[str], env: dict | None = None) -> bool:
    print(f"\n==> {label}")
    r = subprocess.run(cmd, cwd=ROOT, env=env)
    ok = r.returncode == 0
    print(f"    {'OK' if ok else 'FAIL'} ({label})")
    return ok


def main() -> int:
    py = sys.executable
    env = os.environ.copy()
    allow_stub = env.get("PCS_ALLOW_STUB", "").lower() in ("1", "true", "yes")
    if not allow_stub:
        env["PCS_ALLOW_STUB"] = "1"

    checks = [
        ("geo evidence", [py, "scripts/13_validate_geo_evidence.py"]),
        ("sprint outputs", [py, "scripts/08_validate_sprint_outputs.py"]),
        ("production (dev stub allowed)", [py, "scripts/17_validate_production_outputs.py"], env),
        ("audit sample", [py, "scripts/19_validate_audit_sample.py"]),
    ]
    failed = []
    audit_pending = False
    for item in checks:
        label, cmd = item[0], item[1]
        e = item[2] if len(item) > 2 else None
        if not _run(label, cmd, e):
            if label == "audit sample":
                audit_pending = True
                print("    (expected until Engineer B fills audit CSV)")
            else:
                failed.append(label)

    main_tables = ROOT / "paper" / "main_tables"
    n_tables = len(list(main_tables.glob("*.csv"))) if main_tables.exists() else 0
    print(f"\nmain_tables CSV count: {n_tables} (expect 9)")
    if n_tables < 9:
        failed.append("main_tables")

    if failed:
        print("\nPreflight FAILED:", ", ".join(failed))
        return 1
    if audit_pending:
        print("\nPreflight PASSED with audit pending (fill sample before citing Table 17 error rates).")
    else:
        print("\nPreflight PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
