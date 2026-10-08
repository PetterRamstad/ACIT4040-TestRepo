from .candidate_selection import select_candidates
from .config import INITIAL_ROUND_SIZE
from .models import PreferenceState
from .stability import is_stable


class PreferenceEngine:
    def initial_state(self): return PreferenceState()
    def initial_candidates(self,candidates,round_size=INITIAL_ROUND_SIZE):
        ids=[c.id for c in candidates]
        return select_candidates(ids,PreferenceState(),round_size)
    def update(self,state,feedback):
        v=feedback["value"]; cid=feedback["candidate_id"]
        if v=="like" and cid not in state.liked: state.liked.append(cid)
        if v=="dislike" and cid not in state.disliked: state.disliked.append(cid)
        state.round_number+=1; state.uncertainty=max(0.0,1.0-0.18*len(state.liked)-0.12*len(state.disliked))
        state.confidence=1-state.uncertainty; state.stable=is_stable(state)
        state.history.append({"candidate_id":cid,"value":v,"round":state.round_number})
        return state
    def next_candidates(self,state,candidates):
        if state.stable: return []
        return select_candidates([c.id for c in candidates],state,INITIAL_ROUND_SIZE)
    def is_stable(self,state): return is_stable(state)
