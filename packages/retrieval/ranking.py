def rank(items,preference=None):
    return sorted(items,key=lambda x:x.get("score",0),reverse=True)
