from packages.preference.engine import PreferenceEngine
from packages.retrieval.providers.fixture import FixtureFurnitureProvider


class PreferenceService:
    def __init__(self):
        self.engine=PreferenceEngine()
        self.provider=FixtureFurnitureProvider()
        self.state=self.engine.initial_state()

    def candidates(self): return self.provider.list_items()

    def start_round(self):
        return self.engine.initial_candidates(self.candidates()) if self.state.round_number==0 else self.engine.next_candidates(self.state,self.candidates())

    def feedback(self, feedback):
        self.state=self.engine.update(self.state,feedback)
        return self.state

    def response(self): return self.state

service=PreferenceService()
