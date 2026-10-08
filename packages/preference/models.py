from dataclasses import dataclass,field

@dataclass
class PreferenceState:
    round_number:int=0
    confidence:float=0.0
    uncertainty:float=1.0
    stable:bool=False
    liked:list[str]=field(default_factory=list)
    disliked:list[str]=field(default_factory=list)
    history:list[dict]=field(default_factory=list)

@dataclass
class PreferenceCandidate:
    id:str
    score:float
    exploratory:bool=False
