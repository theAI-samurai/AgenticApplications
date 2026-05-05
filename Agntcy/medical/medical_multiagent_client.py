"""
Client for the medical multi-agent demo.

Run after the combined server is active:
    python medical_multiagent_client.py
"""

from __future__ import annotations

import asyncio
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from medical_directory import directory


def _extract_result_text(result: Any) -> str:
    chunks: list[str] = []
    for item in getattr(result, "content", []) or []:
        text = getattr(item, "text", None)
        if text is not None:
            chunks.append(str(text))
        else:
            chunks.append(str(item))
    return "\n".join(chunks) if chunks else str(result)


async def discover_agent(name: str) -> str:
    await directory.setup()
    matches = await directory.search_agent_records(name)
    if not matches:
        raise RuntimeError(f"No agent named '{name}' found. Is server running?")

    from agntcy_app_sdk.directory.oasf_converter import oasf_to_agent_card

    agent_card = oasf_to_agent_card(matches[-1])
    if agent_card is None or not getattr(agent_card, "url", None):
        raise RuntimeError(f"Agent '{name}' found but has no usable AgentCard URL")

    return agent_card.url


async def call_agent_tool(agent_url: str, tool_name: str, params: dict[str, Any]) -> str:
    async with streamablehttp_client(agent_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, params)
            return _extract_result_text(result)


async def main() -> None:
    print("=== Medical Multi-Agent Demo (Agntcy + MCP) ===\n")

    triage_url = await discover_agent("MedicalTriageAgent")
    medication_url = await discover_agent("MedicationSafetyAgent")

    print(f"Discovered MedicalTriageAgent at: {triage_url}")
    print(f"Discovered MedicationSafetyAgent at: {medication_url}\n")

    triage_result = await call_agent_tool(
        triage_url,
        "triage_patient",
        {
            "age": 39,
            "symptoms": "Persistent dry cough with mild chest discomfort and fatigue",
            "duration_days": 5,
            "chronic_conditions": "seasonal asthma",
        },
    )
    specialist = await call_agent_tool(
        triage_url,
        "recommend_specialist",
        {"symptoms": "Persistent dry cough with mild chest discomfort and fatigue"},
    )

    followup_plan = await call_agent_tool(
        medication_url,
        "care_plan_from_triage",
        {
            "triage_summary": triage_result,
            "current_meds": "albuterol inhaler as needed",
            "allergies": "penicillin",
        },
    )

    med_check = await call_agent_tool(
        medication_url,
        "medication_safety_check",
        {
            "allergies": "penicillin",
            "current_meds": "albuterol inhaler as needed",
            "new_medication": "ibuprofen",
        },
    )

    print("--- TRIAGE RESULT ---")
    print(triage_result)
    print()
    print("--- SPECIALIST SUGGESTION ---")
    print(specialist)
    print()
    print("--- FOLLOW-UP CARE PLAN ---")
    print(followup_plan)
    print()
    print("--- MEDICATION SAFETY CHECK ---")
    print(med_check)


if __name__ == "__main__":
    asyncio.run(main())
