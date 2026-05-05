"""Directory configuration for the medical multi-agent demo."""

from __future__ import annotations

import os

from local_directory import LocalDirectory


def _is_truthy(raw: str | None, default: bool = True) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def build_directory():
    use_file_directory = _is_truthy(os.getenv("MEDICAL_USE_FILE_DIRECTORY"), default=True)
    if use_file_directory:
        registry_file = os.getenv("MEDICAL_REGISTRY_FILE", "medical_agent_registry.json")
        return LocalDirectory(registry_file=registry_file)

    endpoint = os.getenv("AGNTCY_DIRECTORY_ENDPOINT") or os.getenv(
        "DIRECTORY_DAEMON_SERVER_LISTEN_ADDRESS",
        "127.0.0.1:8888",
    )
    from agntcy_app_sdk.directory import AgentDirectory

    return AgentDirectory.from_config(endpoint=endpoint)


directory = build_directory()
