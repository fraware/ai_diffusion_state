"""Shared OpenXLab client bootstrap (credentials from environment only)."""
from __future__ import annotations

import os
import re
from pathlib import Path


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


def _list_dataset_objects(client, *, dataset_repo: str, source_path: str) -> tuple[list[dict], str]:
    parsed_ds_name = dataset_repo.replace("/", ",")
    source_path = re.sub(r"^\.+", "", source_path)
    get_payload = {"prefix": source_path}
    after = None
    limit = 500
    all_files: list[dict] = []
    info_dataset_id = ""
    has_more = True
    while has_more:
        data_dict = client.get_api().get_dataset_files(
            dataset_name=parsed_ds_name,
            payload=get_payload,
            needContent=True,
            after=after,
            limit=limit,
        )
        if after is None and data_dict["list"]:
            info_dataset_id = data_dict["list"][0]["dataset_id"]
        all_files.extend(data_dict["list"])
        has_more = data_dict.get("hasNext", False)
        if has_more:
            after = data_dict.get("after")

    object_info_list: list[dict] = []
    for info in all_files:
        name = info["path"][1:]
        if info["path"].startswith("//"):
            name = info["path"][2:]
        object_info_list.append(
            {
                "size": info["size"],
                "name": name,
                "sha256": info.get("sha256", ""),
            }
        )
    if not object_info_list:
        raise FileNotFoundError(f"No files found at {source_path} in {dataset_repo}")
    if not info_dataset_id:
        raise RuntimeError(f"Could not resolve dataset_id for {dataset_repo}")
    return object_info_list, info_dataset_id


def download_dataset_file(
    *,
    dataset_repo: str,
    source_path: str,
    target_path: Path,
    skip_download_check: bool = True,
) -> Path:
    """Download one OpenXLab dataset path to target_path.

    By default skips downloadCheck, which returns HTTP 405 from Aliyun WAF on some networks
    even when signed OSS download URLs work.
    """
    from openxlab.dataset.commands.utility import ContextInfoNoLogin
    from openxlab.dataset.handler.get_dataset_repository import process_download_files

    login_openxlab()
    target_path = target_path.expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    parsed_save_path = dataset_repo.replace("/", "___")

    ctx = ContextInfoNoLogin()
    client = ctx.get_client()
    object_info_list, info_dataset_id = _list_dataset_objects(
        client,
        dataset_repo=dataset_repo,
        source_path=source_path,
    )

    if not skip_download_check:
        download_check_path = object_info_list[0]["name"]
        client.get_api().download_check(dataset_id=info_dataset_id, path=download_check_path)
    else:
        print(
            "Skipping OpenXLab downloadCheck preflight "
            "(Aliyun WAF 405 workaround; using signed OSS URLs directly)."
        )

    _obj, local_file_path = process_download_files(
        client,
        object_info_list,
        str(target_path),
        parsed_save_path,
        info_dataset_id,
    )
    client.get_api().track_download_dataset_files(
        dataset_name=dataset_repo.replace("/", ","),
        file_path=source_path,
    )
    return Path(local_file_path)
