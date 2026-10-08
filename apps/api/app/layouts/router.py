from fastapi import APIRouter
from packages.layout.models import Room,Layout,Placement
from packages.layout.constraints import LayoutValidator
from packages.layout.generator import LayoutEngine
from packages.retrieval.providers.fixture import FixtureFurnitureProvider
router=APIRouter(prefix="/layouts",tags=["layouts"])
@router.post("/validate")
def validate(payload:dict):
    room=Room(**payload["room"]); layout=Layout([Placement(**p) for p in payload.get("placements",[])]); return LayoutValidator().validate(room,layout)
@router.post("/generate")
def generate(payload:dict):
    room=Room(**payload["room"]); items=FixtureFurnitureProvider().list_items(); layout=LayoutEngine().generate(room,items); return {"status":"completed","placements":[p.__dict__ for p in layout.placements]}
