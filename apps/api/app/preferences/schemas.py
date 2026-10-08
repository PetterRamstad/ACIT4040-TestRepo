from pydantic import BaseModel, Field

class Feedback(BaseModel):
    candidate_id:str
    value:str=Field(pattern="^(like|neutral|dislike)$")

class StartRound(BaseModel):
    candidate_ids:list[str]|None=None

class PreferenceStateResponse(BaseModel):
    round_number:int
    confidence:float
    uncertainty:float
    stable:bool
    liked:list[str]
    disliked:list[str]
