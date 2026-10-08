from .config import STABILITY_UNCERTAINTY
from .models import PreferenceState


def is_stable(state:PreferenceState)->bool:
    return state.round_number>=2 and state.uncertainty<=STABILITY_UNCERTAINTY
