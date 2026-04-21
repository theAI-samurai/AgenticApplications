"""
OASF (Open Agentic Schema Framework) - Agent Record Definition

An OASF record describes an AI agent's capabilities, metadata, and skills
in a standardized, interoperable format. This is the foundation for agent
discovery across distributed systems.
"""

from dataclasses import dataclass, field
from typing import Any

from a2a.types import AgentCard, AgentCapabilities, AgentSkill


@dataclass
class OASFSkill:
    """Represents a single capability the agent has."""
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class OASFRecord:
    """
    OASF Agent Record — standard metadata structure for AI agents.
    Inspired by OCSF (Open Cybersecurity Schema Framework).
    """
    # Identity
    name: str
    version: str
    description: str
    author: str

    # Taxonomy
    domain: str          # e.g. "productivity", "data-analysis", "customer-support"
    category: str        # e.g. "tool-use", "reasoning", "retrieval"

    # Capabilities
    skills: list[OASFSkill] = field(default_factory=list)
    input_modes: list[str] = field(default_factory=lambda: ["text"])
    output_modes: list[str] = field(default_factory=lambda: ["text"])
    streaming: bool = False

    # Extensions (arbitrary metadata — OASF is extensible)
    extensions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "domain": self.domain,
            "category": self.category,
            "skills": [
                {
                    "name": s.name,
                    "description": s.description,
                    "input_schema": s.input_schema,
                    "output_schema": s.output_schema,
                }
                for s in self.skills
            ],
            "input_modes": self.input_modes,
            "output_modes": self.output_modes,
            "streaming": self.streaming,
            "extensions": self.extensions,
        }

    def to_agent_card(self, url: str) -> AgentCard:
        """
        Convert this OASF record to an A2A AgentCard so it can be pushed
        to the Agntcy Directory and discovered by other agents.

        Parameters
        ----------
        url:
            The HTTP endpoint where the agent's MCP server is reachable
            (e.g. "http://localhost:8000/mcp").
        """
        return AgentCard(
            name=self.name,
            description=self.description,
            version=self.version,
            url=url,
            defaultInputModes=self.input_modes,
            defaultOutputModes=self.output_modes,
            capabilities=AgentCapabilities(streaming=self.streaming),
            skills=[
                AgentSkill(
                    id=s.name,
                    name=s.name,
                    description=s.description,
                    tags=[s.name],
                    inputModes=self.input_modes,
                    outputModes=self.output_modes,
                )
                for s in self.skills
            ],
        )


# ── Define the agent record for our demo "Calculator Agent" ──────────────────

calculator_record = OASFRecord(
    name="CalculatorAgent",
    version="1.0.0",
    description="A simple agent that performs arithmetic and unit conversions.",
    author="demo",
    domain="productivity",
    category="tool-use",
    skills=[
        OASFSkill(
            name="add",
            description="Add two numbers together",
            input_schema={"a": "number", "b": "number"},
            output_schema={"result": "number"},
        ),
        OASFSkill(
            name="multiply",
            description="Multiply two numbers",
            input_schema={"a": "number", "b": "number"},
            output_schema={"result": "number"},
        ),
        OASFSkill(
            name="celsius_to_fahrenheit",
            description="Convert a temperature from Celsius to Fahrenheit",
            input_schema={"celsius": "number"},
            output_schema={"fahrenheit": "number"},
        ),
    ],
    streaming=False,
    extensions={"license": "Apache-2.0", "tags": ["math", "conversion"]},
)


if __name__ == "__main__":
    import json
    print("=== OASF Agent Record ===")
    print(json.dumps(calculator_record.to_dict(), indent=2))
