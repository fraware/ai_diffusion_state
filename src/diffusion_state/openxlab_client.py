"""Shared OpenXLab client bootstrap (credentials from environment only)."""
from __future__ import annotations

import os


def configure_openxlab_ssl() -> None:
    if os.environ.get("OPENXLAB_INSECURE_SSL", "").lower() not in ("1", "true", "yes"):
        return
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    import requests

    _orig = requests.Session.request

    def _request(session, method, url, **kwargs):  # noqa: ANN001
        kwargs.setdefault("verify", False)
        return _orig(session, method, url, **kwargs)

    requests.Session.request = _request  # type: ignore[method-assign]


def login_openxlab() -> None:
    ak = os.environ.get("OPENXLAB_AK")
    sk = os.environ.get("OPENXLAB_SK")
    if not ak or not sk:
        raise SystemExit(
            "Missing OPENXLAB_AK / OPENXLAB_SK environment variables. "
            "Set them locally; do not commit credentials."
        )
    configure_openxlab_ssl()
    if os.environ.get("OPENXLAB_INSECURE_SSL", "").lower() in ("1", "true", "yes"):
        print("WARNING: OPENXLAB_INSECURE_SSL=1 — TLS certificate verification disabled for this run.")
    import openxlab

    openxlab.login(ak=ak, sk=sk)
