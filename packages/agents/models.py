from dataclasses import dataclass


@dataclass(frozen=True)
class AgentAction: name:str; reason:str
