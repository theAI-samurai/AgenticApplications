"""
Shared directory singleton.

Uses a JSON file (agent_registry.json) as the backing store so both the
agent process (push) and the client process (search/pull) share state on disk.

To switch to a real agntcy-dir gRPC service, replace LocalDirectory with:

    from agntcy_app_sdk.directory import AgentDirectory
    directory = AgentDirectory.from_config(endpoint="127.0.0.1:8888")
"""

from local_directory import LocalDirectory

REGISTRY_FILE = "agent_registry.json"

directory = LocalDirectory(registry_file=REGISTRY_FILE)
