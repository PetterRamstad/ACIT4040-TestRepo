from fastapi import APIRouter

from packages.agents.orchestrator import AgentOrchestrator

router=APIRouter(prefix="/agent",tags=["agent"])
@router.post("/next")
def next_action(payload:dict):
    class S: stable=bool(payload.get("stable",False))
    return AgentOrchestrator().next_action(S()).__dict__
