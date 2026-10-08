class QdrantVectorStore:
    def __init__(self): self.collections={}
    def ensure_collection(self,name,dimension,version): self.collections.setdefault(name,{"dimension":dimension,"version":version,"records":{}})
    def upsert(self,collection,records): self.collections[collection]["records"].update(records)
    def search(self,collection,vector,limit=10):
        import math
        rec=self.collections.get(collection,{"records":{}})["records"]
        def sim(v): return sum(a*b for a,b in zip(v,vector))/(math.sqrt(sum(a*a for a in v))*math.sqrt(sum(b*b for b in vector)) or 1)
        return sorted(((k,sim(v)) for k,v in rec.items()),key=lambda x:x[1],reverse=True)[:limit]
