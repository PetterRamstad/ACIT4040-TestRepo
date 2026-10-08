from packages.layout.constraints import LayoutValidator
from packages.preference.engine import PreferenceEngine
from packages.retrieval.retriever import FurnitureRetriever


class AgentTools:
    def __init__(self): self.preference=PreferenceEngine(); self.retrieval=FurnitureRetriever(); self.validator=LayoutValidator()
