from fastapi import APIRouter

from .schemas import Feedback, PreferenceStateResponse
from .service import service

router=APIRouter(prefix="/preferences",tags=["preferences"])

@router.get("/state",response_model=PreferenceStateResponse)
def state(): return service.response()

@router.post("/rounds")
def rounds(): return {"round":service.start_round()}

@router.post("/feedback",response_model=PreferenceStateResponse)
def feedback(payload:Feedback): return service.feedback(payload.model_dump())

@router.get("/history")
def history(): return {"rounds":service.state.history}

@router.post("/next-candidates")
def next_candidates(): return {"round":service.start_round()}
