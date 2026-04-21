"""OASF records for the medical multi-agent demo."""

from oasf_record import OASFRecord, OASFSkill


medical_triage_record = OASFRecord(
    name="MedicalTriageAgent",
    version="1.0.0",
    description=(
        "Assesses symptom urgency and suggests the right care pathway. "
        "For educational demo use only."
    ),
    author="demo",
    domain="healthcare",
    category="triage",
    skills=[
        OASFSkill(
            name="triage_patient",
            description="Generate a symptom triage summary and urgency recommendation",
            input_schema={
                "age": "integer",
                "symptoms": "string",
                "duration_days": "integer",
                "chronic_conditions": "string",
            },
            output_schema={"summary": "string"},
        ),
        OASFSkill(
            name="recommend_specialist",
            description="Recommend a specialist based on symptoms",
            input_schema={"symptoms": "string"},
            output_schema={"specialist": "string"},
        ),
        OASFSkill(
            name="emergency_red_flags",
            description="Check if symptoms include emergency warning signals",
            input_schema={"symptoms": "string"},
            output_schema={"guidance": "string"},
        ),
    ],
    streaming=False,
    extensions={"tags": ["medical", "triage", "healthcare"]},
)


medication_safety_record = OASFRecord(
    name="MedicationSafetyAgent",
    version="1.0.0",
    description=(
        "Provides high-level medication safety and follow-up guidance from "
        "triage context. For educational demo use only."
    ),
    author="demo",
    domain="healthcare",
    category="medication-safety",
    skills=[
        OASFSkill(
            name="medication_safety_check",
            description="Review allergy and medication conflict risk at high level",
            input_schema={
                "allergies": "string",
                "current_meds": "string",
                "new_medication": "string",
            },
            output_schema={"assessment": "string"},
        ),
        OASFSkill(
            name="care_plan_from_triage",
            description="Create a next-step care plan from triage summary",
            input_schema={
                "triage_summary": "string",
                "current_meds": "string",
                "allergies": "string",
            },
            output_schema={"plan": "string"},
        ),
    ],
    streaming=False,
    extensions={"tags": ["medical", "medication", "safety"]},
)
