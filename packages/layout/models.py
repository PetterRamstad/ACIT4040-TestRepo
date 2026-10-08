from dataclasses import dataclass, field


@dataclass(frozen=True)
class Room: width:float; depth:float; doors:list[tuple[float,float,float,float]]=field(default_factory=list)
@dataclass(frozen=True)
class Placement: furniture_id:str; x:float; y:float; width:float; depth:float
@dataclass
class Layout: placements:list[Placement]
