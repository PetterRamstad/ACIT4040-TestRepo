from fastapi import APIRouter, HTTPException

from .schemas import FurnitureFeedback
from .service import service

router=APIRouter(prefix="/furniture",tags=["furniture"])
@router.get("")
def list_furniture(): return service.list()
@router.get("/{item_id}")
def get_furniture(item_id):
    try:return service.get(item_id)
    except KeyError: raise HTTPException(404,"Unknown furniture ID")
@router.post("/{item_id}/feedback")
def feedback(item_id,payload:FurnitureFeedback): service.get(item_id); return {"ok":True,"furniture_id":item_id,"value":payload.value}
