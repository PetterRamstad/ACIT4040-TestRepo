from .models import PreferenceState
from .config import STABILITY_UNCERTAINTY
def is_stable(state:PreferenceState)->bool:
    return state.round_number>=2 and state.uncertainty<=STABILITY_UNCERTAINTY
