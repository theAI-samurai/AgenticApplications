"""OASF (Open Agentic Schema Framework) record definition for simple demo."""

from dataclasses import dataclass, field
from typing import Any

from a2a.types import AgentCard, AgentCapabilities, AgentSkill


@dataclass
class OASFSkill:
    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class OASFRecord:
    name: str
    version: str
    description: str
    author: str
    domain: str
    category: str
    skills: list[OASFSkill] = field(default_factory=list)
    input_modes: list[str] = field(default_factory=lambda: ["text"])
    output_modes: list[str] = field(default_factory=lambda: ["text"])
    streaming: bool = False
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
