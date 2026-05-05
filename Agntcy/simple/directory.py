"""Shared directory singleton for the simple demo."""

from local_directory import LocalDirectory

REGISTRY_FILE = "agent_registry.json"

directory = LocalDirectory(registry_file=REGISTRY_FILE)
