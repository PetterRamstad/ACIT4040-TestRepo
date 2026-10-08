from packages.layout.constraints import LayoutValidator
from packages.retrieval.retriever import FurnitureRetriever
from packages.preference.engine import PreferenceEngine
class AgentTools:
    def __init__(self): self.preference=PreferenceEngine(); self.retrieval=FurnitureRetriever(); self.validator=LayoutValidator()
