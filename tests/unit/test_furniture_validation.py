from packages.retrieval.furniture_models import FurnitureItem
from packages.retrieval.furniture_validation import validate_furniture


def test_positive_dimensions(): assert validate_furniture(FurnitureItem("x","fixture","x",dimensions=(1,1,1))).id=="x"
def test_invalid_dimensions():
 try: validate_furniture(FurnitureItem("x","fixture","x",dimensions=(0,1,1))); assert False
 except ValueError: assert True
