from .config import INITIAL_ROUND_SIZE, LIKELY_RATIO
from .models import PreferenceCandidate, PreferenceState


def select_candidates(ids:list[str],state:PreferenceState,size:int=INITIAL_ROUND_SIZE)->list[PreferenceCandidate]:
    pool=[i for i in ids if i not in state.liked and i not in state.disliked]
    if len(pool)<size: raise ValueError(f"Need {size} usable candidates, got {len(pool)}")
    likely_n=int(size*LIKELY_RATIO)
    return [PreferenceCandidate(i,1.0-j*0.01,j>=likely_n) for j,i in enumerate(pool[:size])]
