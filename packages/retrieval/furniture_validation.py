def validate_furniture(item):
    if any(x<=0 for x in item.dimensions): raise ValueError("dimensions must be positive")
    return item
