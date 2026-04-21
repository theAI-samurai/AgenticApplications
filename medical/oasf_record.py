"""Shared OASF record types used by the medical demo."""

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
