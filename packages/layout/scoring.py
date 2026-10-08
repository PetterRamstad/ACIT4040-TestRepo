def score(room,layout,preference=None): return 1.0 if layout.placements else 0.0
class LayoutScorer:
    def score(self,room,layout,preference=None): return score(room,layout,preference)
