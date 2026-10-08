import json
from pathlib import Path
from packages.retrieval.furniture_models import FurnitureItem

class FixtureFurnitureProvider:
    def __init__(self,path=None): self.path=Path(path or "data/fixtures/furniture.json")
    def list_items(self):
        raw=json.loads(self.path.read_text())
        return [FurnitureItem(id=x["id"],source=x["source"],source_id=x["source_id"],name=x.get("name"),category=x.get("category"),room_types=tuple(x.get("room_types",[])),style=tuple(x.get("style",[])),colors=tuple(x.get("colors",[])),materials=tuple(x.get("materials",[])),dimensions=tuple(x.get("dimensions",[1,1,1])),image_path=x.get("image_path"),model_path=x.get("model_path")) for x in raw]
    def get_item(self,item_id):
        for x in self.list_items():
            if x.id==item_id:return x
        raise KeyError(item_id)
