class CompatibilityService:
    def score(self,items,context=None):
        return sorted(items,key=lambda x:x.get("compatibility",0),reverse=True)
