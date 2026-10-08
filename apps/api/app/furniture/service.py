from packages.retrieval.providers.fixture import FixtureFurnitureProvider
class FurnitureService:
    def __init__(self): self.provider=FixtureFurnitureProvider()
    def list(self): return self.provider.list_items()
    def get(self,id): return self.provider.get_item(id)
service=FurnitureService()
