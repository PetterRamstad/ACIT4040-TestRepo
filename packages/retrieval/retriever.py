from .providers.fixture import FixtureFurnitureProvider


class FurnitureRetriever:
    def __init__(self,provider=None): self.provider=provider or FixtureFurnitureProvider()
    def retrieve(self,preference=None,filters=None,limit=10):
        items=self.provider.list_items()
        filters=filters or {}
        def ok(i): return all(getattr(i,k,None)==v or v in (getattr(i,k,()) or ()) for k,v in filters.items())
        return [ {"item":i,"score":1.0/(idx+1),"reason":"fixture preference match"} for idx,i in enumerate([x for x in items if ok(x)])][:limit]
