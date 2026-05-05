"""
LocalDirectory — a file-backed implementation of BaseAgentDirectory.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from agntcy_app_sdk.directory.base import BaseAgentDirectory, RecordVisibility
from agntcy_app_sdk.directory.oasf_converter import agent_card_to_oasf, oasf_to_agent_card
from agntcy_app_sdk.common.logging_config import get_logger
from a2a.types import AgentCard

logger = get_logger(__name__)


def _cid(record: dict[str, Any]) -> str:
    blob = json.dumps(record, sort_keys=True, default=str).encode()
    return "sha256:" + hashlib.sha256(blob).hexdigest()[:16]


class LocalDirectory(BaseAgentDirectory):
    DIRECTORY_TYPE: str = "local"

    @classmethod
    def from_config(cls, endpoint: str | None = None, **kwargs: Any) -> "LocalDirectory":
        return cls()

    def __init__(self, registry_file: str | None = None) -> None:
        self._registry_file = registry_file
        self._records: dict[str, dict[str, Any]] = {}

    def _load(self) -> None:
        if self._registry_file and os.path.exists(self._registry_file):
            with open(self._registry_file) as f:
                self._records = json.load(f)

    def _save(self) -> None:
        if self._registry_file:
            with open(self._registry_file, "w") as f:
                json.dump(self._records, f, indent=2)

    async def setup(self) -> None:
        self._load()
        logger.info(
            "LocalDirectory: ready (%s records from %s)",
            len(self._records),
            self._registry_file or "memory",
        )

    async def teardown(self) -> None:
        self._save()
        self._records.clear()
        logger.info("LocalDirectory: saved and cleared")

    async def push_agent_record(
        self,
        record: Any,
        visibility: RecordVisibility = RecordVisibility.PUBLIC,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        if isinstance(record, AgentCard):
            oasf_dict = agent_card_to_oasf(record)
        elif isinstance(record, dict):
            oasf_dict = record
        else:
            raise TypeError(f"Unsupported record type: {type(record).__name__}")

        self._load()
        cid = _cid(oasf_dict)
        self._records[cid] = oasf_dict
        self._save()
        logger.info("LocalDirectory: pushed '%s' -> CID %s", oasf_dict.get("name"), cid)
        return cid

    async def pull_agent_record(
        self,
        ref: Any,
        *args: Any,
        extract_card: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | AgentCard | None:
        self._load()
        cid = ref if isinstance(ref, str) else str(ref)
        oasf_dict = self._records.get(cid)
        if oasf_dict is None:
            return None
        if extract_card:
            card = oasf_to_agent_card(oasf_dict)
            if card is not None:
                return card
        return oasf_dict

    async def search_agent_records(
        self,
        query: Any,
        limit: int = 10,
        *args: Any,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        self._load()
        results: list[dict[str, Any]] = []
        for record in self._records.values():
            if isinstance(query, str):
                if query.lower() in record.get("name", "").lower():
                    results.append(record)
            elif isinstance(query, dict):
                if all(record.get(k) == v for k, v in query.items()):
                    results.append(record)
            if len(results) >= limit:
                break
        return results

    async def delete_agent_record(self, ref: Any, *args: Any, **kwargs: Any) -> None:
        self._load()
        cid = ref if isinstance(ref, str) else str(ref)
        self._records.pop(cid, None)
        self._save()

    async def list_agent_records(self, *args: Any, **kwargs: Any) -> list:
        self._load()
        return list(self._records.values())

    async def sign_agent_record(self, record_ref: Any, provider: Any, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    async def verify_agent_record(self, record_ref: Any) -> None:
        raise NotImplementedError

    async def get_record_visibility(self, ref: Any, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError

    async def set_record_visibility(self, ref: Any, visibility: RecordVisibility, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError
