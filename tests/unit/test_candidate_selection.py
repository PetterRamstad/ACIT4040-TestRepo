from packages.preference.candidate_selection import select_candidates
from packages.preference.models import PreferenceState
def test_70_30_default():
 out=select_candidates([str(i) for i in range(10)],PreferenceState(),5); assert sum(x.exploratory for x in out)==2
