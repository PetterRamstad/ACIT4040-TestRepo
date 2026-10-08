from packages.preference.engine import PreferenceEngine
from packages.retrieval.providers.fixture import FixtureFurnitureProvider


def test_initial_round_has_five():
 e=PreferenceEngine(); assert len(e.initial_candidates(FixtureFurnitureProvider().list_items()))==5
def test_feedback_reduces_uncertainty():
 e=PreferenceEngine(); s=e.initial_state(); old=s.uncertainty; s=e.update(s,{"candidate_id":"chair-001","value":"like"}); assert s.uncertainty<old
