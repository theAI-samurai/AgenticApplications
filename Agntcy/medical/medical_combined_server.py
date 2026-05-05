"""
Combined MCP server for the medical multi-agent demo.

Run:
    python medical_combined_server.py
"""

from __future__ import annotations

import asyncio
import os

from mcp.server.fastmcp import FastMCP

from medical_directory import directory
from medical_oasf_records import medical_triage_record, medication_safety_record


COMBINED_PORT = int(os.getenv("MEDICAL_COMBINED_PORT", "8100"))
COMBINED_URL = os.getenv("MEDICAL_COMBINED_URL", f"http://127.0.0.1:{COMBINED_PORT}/mcp")


mcp = FastMCP(
    name="MedicalCombinedAgentServer",
    instructions=(
        "Combined medical demo endpoint exposing triage and medication safety tools. "
        "Educational use only."
    ),
    host="127.0.0.1",
    port=COMBINED_PORT,
)


@mcp.tool()
def emergency_red_flags(symptoms: str) -> str:
    danger_terms = [
        "chest pain",
        "shortness of breath",
        "fainting",
        "uncontrolled bleeding",
        "stroke",
        "seizure",
    ]
    lowered = symptoms.lower()
    matches = [term for term in danger_terms if term in lowered]
    if matches:
        return (
            "Potential emergency red flags detected: "
            + ", ".join(matches)
            + ". Seek urgent in-person care now."
        )
    return "No immediate emergency keywords detected from provided symptoms."


@mcp.tool()
def recommend_specialist(symptoms: str) -> str:
    lowered = symptoms.lower()
    if "skin" in lowered or "rash" in lowered:
        return "Dermatology"
    if "headache" in lowered or "numbness" in lowered:
        return "Neurology"
    if "cough" in lowered or "breath" in lowered:
        return "Pulmonology"
    if "stomach" in lowered or "abdominal" in lowered:
        return "Gastroenterology"
    return "Primary Care"


@mcp.tool()
def triage_patient(
    age: int,
    symptoms: str,
    duration_days: int,
    chronic_conditions: str = "none",
) -> str:
    urgency = "routine"
    lowered = symptoms.lower()

    if any(token in lowered for token in ["chest pain", "shortness of breath", "fainting"]):
        urgency = "urgent"
    elif duration_days >= 7 or any(token in lowered for token in ["fever", "persistent"]):
        urgency = "priority"

    specialist = recommend_specialist(symptoms)
    red_flags = emergency_red_flags(symptoms)

    return (
        "Medical demo triage summary\n"
        f"- Age: {age}\n"
        f"- Symptoms: {symptoms}\n"
        f"- Duration days: {duration_days}\n"
        f"- Chronic conditions: {chronic_conditions}\n"
        f"- Urgency: {urgency}\n"
        f"- Suggested specialist: {specialist}\n"
        f"- Safety note: {red_flags}\n"
        "- Disclaimer: Educational demo only, not a diagnosis."
    )


@mcp.tool()
def medication_safety_check(
    allergies: str,
    current_meds: str,
    new_medication: str,
) -> str:
    allergy_text = allergies.lower()
    med_text = current_meds.lower()
    candidate = new_medication.lower()

    if candidate and candidate in allergy_text:
        return (
            f"Potential allergy conflict: '{new_medication}' appears in allergy list. "
            "Do not start and consult a clinician or pharmacist immediately."
        )

    if "warfarin" in med_text and any(x in candidate for x in ["ibuprofen", "aspirin"]):
        return (
            "Potential interaction risk detected with anticoagulant context. "
            "Request professional medication review before use."
        )

    return (
        "No direct keyword conflict detected in this demo check. "
        "Still confirm dosage and interactions with a licensed clinician or pharmacist."
    )


@mcp.tool()
def care_plan_from_triage(
    triage_summary: str,
    current_meds: str,
    allergies: str = "none",
) -> str:
    summary = triage_summary.lower()
    follow_up = "book a primary care visit in 2-3 days"

    if "urgency: urgent" in summary:
        follow_up = "seek same-day urgent care or emergency evaluation"
    elif "urgency: priority" in summary:
        follow_up = "schedule clinician evaluation within 24 hours"

    return (
        "Medication safety and follow-up plan\n"
        f"- Current meds: {current_meds}\n"
        f"- Allergies: {allergies}\n"
        f"- Recommended follow-up: {follow_up}\n"
        "- Safety checks: avoid adding new OTC medicines without interaction review\n"
        "- Disclaimer: Educational demo only, not medical advice."
    )


async def _register_both() -> tuple[str, str]:
    await directory.setup()
    triage_card = medical_triage_record.to_agent_card(url=COMBINED_URL)
    medication_card = medication_safety_record.to_agent_card(url=COMBINED_URL)
    triage_cid = await directory.push_agent_record(triage_card)
    medication_cid = await directory.push_agent_record(medication_card)
    return triage_cid, medication_cid


if __name__ == "__main__":
    triage_cid, medication_cid = asyncio.run(_register_both())
    print("Starting MedicalCombinedAgentServer v1.0.0")
    print(f"[Directory] Registered {medical_triage_record.name} -> CID: {triage_cid}")
    print(f"[Directory] Registered {medication_safety_record.name} -> CID: {medication_cid}")
    print(f"Server listening on {COMBINED_URL} (Ctrl+C to stop)")
    mcp.run(transport="streamable-http")
