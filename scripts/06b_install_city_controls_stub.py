"""Deprecated: CI stub controls are not used in this repository pipeline."""
from __future__ import annotations

import sys


def main() -> int:
    print(
        "ERROR: city-controls-stub is disabled. Use production EPS/NBS via make city-controls.\n"
        "To remove leftover stub files: make purge-stub-controls"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
