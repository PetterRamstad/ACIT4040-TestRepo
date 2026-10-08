from fastapi import APIRouter, HTTPException

from .schemas import RoomCreate

rooms: dict[str, dict[str, object]] = {}
router=APIRouter(prefix="/rooms",tags=["rooms"])
@router.post("")
def create_room(payload:RoomCreate):
    rid=f"room-{len(rooms)+1}"; rooms[rid]=payload.model_dump(); return {"id":rid,**rooms[rid]}
@router.get("/{room_id}")
def get_room(room_id):
    if room_id not in rooms: raise HTTPException(404,"Unknown room")
    return {"id":room_id,**rooms[room_id]}
