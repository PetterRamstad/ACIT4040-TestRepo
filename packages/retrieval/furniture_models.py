from dataclasses import dataclass

@dataclass(frozen=True)
class FurnitureItem:
    id:str; source:str; source_id:str; name:str|None=None; category:str|None=None; room_types:tuple[str,...]=(); style:tuple[str,...]=(); colors:tuple[str,...]=(); materials:tuple[str,...]=(); dimensions:tuple[float,float,float]=(1,1,1); image_path:str|None=None; model_path:str|None=None; embedding_id:str|None=None
